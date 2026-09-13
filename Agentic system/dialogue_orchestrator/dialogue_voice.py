"""The duplex voice conversation, over /ws.

The client streams 16 kHz PCM16 audio and runs voice activity detection on its
own side, so it decides when the chat participant starts and stops speaking,
including barge-in. Each turn runs the same orchestrator as text chat, and the
reply comes back as 24 kHz PCM speech. Voice pauses at the steps the chat
participant has to read and tap (the snapshot, the action plan, a training
card): there the server sends `voice_mode_exit`, and the interface takes over."""

import asyncio
import base64
import json
import logging
import math
import struct

from fastapi import WebSocket

import dashscope
from dashscope.audio.asr.recognition import (
    Recognition,
    RecognitionCallback,
    RecognitionResult,
)
from dashscope.audio.qwen_tts_realtime import (
    AudioFormat,
    QwenTtsRealtime,
    QwenTtsRealtimeCallback,
)

from config import (
    ASR_ENDPOINT,
    ASR_FORMAT,
    ASR_LANGUAGE_HINTS,
    ASR_MODEL,
    ASR_SAMPLE_RATE,
    ASR_SPEECH_NOISE_THRESHOLD,
    TTS_ENDPOINT,
    TTS_MODEL,
    TTS_VOICE,
    dashscope_api_key,
)
from dialogue_orchestrator.dialogue_orchestrator import (
    DialogueOrchestrator,
    stream_llm_reply,
)
from infrastructure.concurrency_locks import session_lock
from infrastructure.message_protocol import latest_role
from prompts.coping_skills_training import RATING_ASK, RATING_SCALE
from prompts.dialogue_orchestrator import VOICE_GREETING_CONTINUE

logger = logging.getLogger("voice")

dashscope.api_key = dashscope_api_key
dashscope.base_websocket_api_url = ASR_ENDPOINT

UI_REQUIRED = ("get_snapshot", "get_advice", "ask_train", "wait_for_checkin")

def _ring_sound(duration_ms: int = 600, sample_rate: int = 24000,
                volume: float = 0.3) -> bytes:
    n = int(sample_rate * duration_ms / 1000)
    out = bytearray()
    fade = int(sample_rate * 0.02)
    for i in range(n):
        t = i / sample_rate
        sample = (math.sin(2 * math.pi * 400 * t)
                  + math.sin(2 * math.pi * 450 * t)) / 2
        if i < fade:
            sample *= i / fade
        elif i > n - fade:
            sample *= (n - i) / fade
        out.extend(struct.pack("<h", int(sample * 32767 * volume)))
    return bytes(out)

RING = _ring_sound()
GAP = bytes(24000 * 2 * 2 // 10)

class _TtsCallback(QwenTtsRealtimeCallback):
    def __init__(self, ws: WebSocket, loop: asyncio.AbstractEventLoop):
        self.ws = ws
        self.loop = loop

    def on_event(self, response: dict) -> None:
        if response.get("type") == "response.audio.delta":
            data = response.get("delta")
            if data:
                asyncio.run_coroutine_threadsafe(
                    self.ws.send_bytes(base64.b64decode(data)), self.loop)

class _AsrCallback(RecognitionCallback):
    def __init__(self, session: "ConversationSession"):
        self.session = session

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if not sentence:
            return
        text = sentence.get("text", "")
        if not text or self.session.asr_turn_id != self.session.turn_id:
            return
        is_end = RecognitionResult.is_sentence_end(sentence)
        self.session.update_asr_text(text, is_end)
        asyncio.run_coroutine_threadsafe(
            self.session.ws.send_json(
                {"type": "asr_final" if is_end else "asr_partial", "text": text}),
            self.session.loop,
        )


class ConversationSession:
    def __init__(self, ws: WebSocket, user_id: str, session_id: str, storage):
        self.ws = ws
        self.storage = storage
        self.loop = asyncio.get_running_loop()
        self.user_id = user_id
        self.session_id = session_id

        self.turn_id = 0
        self.asr_turn_id = 0
        self.asr_final = self.asr_partial = self.asr_cache = ""
        self.busy: asyncio.Task | None = None

        self.tts = QwenTtsRealtime(
            model=TTS_MODEL,
            callback=_TtsCallback(ws, self.loop),
            url=TTS_ENDPOINT,
        )
        self.tts.connect()
        self._configure_tts()

    def _configure_tts(self) -> None:
        self.tts.update_session(
            voice=TTS_VOICE,
            response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            mode="server_commit",
        )

    def update_asr_text(self, text: str, is_final: bool) -> None:
        if is_final:
            self.asr_final = text
        self.asr_partial = self.asr_cache = text

    def close(self) -> None:
        try:
            self.tts.close()
        except Exception:
            pass

    async def interrupt(self) -> None:
        if self.busy and not self.busy.done():
            self.busy.cancel()
            try:
                await self.busy
            except asyncio.CancelledError:
                pass
        try:
            self.tts.close()
        except Exception:
            pass
        self.tts.connect()
        self._configure_tts()
        await self._send({"type": "audio_interrupt", "action": "stop_immediately"})


    async def say_greeting(self) -> None:
        session = self.storage.load_session(self.session_id)
        if not session:
            return
        for m in reversed(session["messages"]):
            if m["role"] == "assistant":
                text = m["content"]
                if len(text) <= 160:
                    await asyncio.sleep(0.4)
                    self._speak(text)
                else:
                    self._speak(VOICE_GREETING_CONTINUE)
                return

    def _speak(self, text: str) -> None:
        text = self._tts_text(text)
        if text.strip():
            self.tts.append_text(text)
            self.tts.finish()

    @staticmethod
    def _tts_text(text: str) -> str:
        return (text
                .replace(RATING_SCALE, "")
                .replace(RATING_ASK, "Please answer with a number from one to ten.")
                .strip())

    async def start_response(self) -> None:
        await self.interrupt()
        for _ in range(10):
            if self.asr_final or self.asr_cache or self.asr_partial:
                break
            await asyncio.sleep(0.2)
        text = (self.asr_final or self.asr_cache or self.asr_partial).strip()
        self.asr_final = self.asr_cache = self.asr_partial = ""
        if not text:
            return

        session = self.storage.load_session(self.session_id)
        user = self.storage.load_user(self.user_id)
        if not session or not user:
            return

        lock = session_lock(self.session_id)
        await lock.acquire()
        orchestrator = DialogueOrchestrator(session, user, self.storage)
        action = await asyncio.to_thread(orchestrator.handle_turn, text, "audio")
        self.busy = asyncio.create_task(self._answer(session, action, lock))

    async def _answer(self, session: dict, action: dict, lock) -> None:
        try:
            await self._do_answer(session, action)
        finally:
            lock.release()

    async def _do_answer(self, session: dict, action: dict) -> None:
        if action["kind"] == "direct":
            reply = action["reply"]
            await self._send({"type": "llm_delta", "text": reply})
            self._speak(reply)
            if self._needs_text_ui(action.get("events") or []):
                await self._voice_exit(reply)
            return

        full = ""
        async for chunk in stream_llm_reply(session, self.storage):
            full += chunk.get("content", "")
            if chunk.get("done"):
                break
            await self._send({"type": "llm_delta", "text": chunk["content"]})
            self.tts.append_text(self._tts_text(chunk["content"]))
        if not full:
            return
        self.tts.finish()
        stored = latest_role(session, "assistant")
        if self._needs_text_ui(stored.get("events") or []):
            await self._voice_exit(full)

    @staticmethod
    def _needs_text_ui(events: list) -> bool:
        return any(e.get("type") in UI_REQUIRED for e in events if isinstance(e, dict))

    async def _voice_exit(self, content: str) -> None:
        await self._send({"type": "llm_done", "text": content})
        await self._send({"type": "voice_mode_exit",
                          "reason": "user_interaction_required",
                          "full_content": content})

    async def _send(self, payload: dict) -> None:
        try:
            await self.ws.send_json(payload)
        except Exception:
            pass

    async def on_text(self, raw: str) -> None:
        data = json.loads(raw)
        kind = data.get("type")
        if kind == "vad_start":
            self.turn_id += 1
            self.asr_turn_id = self.turn_id
            self.asr_final = self.asr_partial = self.asr_cache = ""
        elif kind == "vad_end":
            await self.start_response()
        elif kind == "interrupt":
            await self.interrupt()

async def voice_endpoint(ws: WebSocket, storage) -> None:
    await ws.accept()

    stop_ring = asyncio.Event()

    async def play_ring():
        while not stop_ring.is_set():
            await ws.send_bytes(RING)
            await asyncio.sleep(0.6)
            if stop_ring.is_set():
                break
            await ws.send_bytes(GAP)
            await asyncio.sleep(0.2)

    ring_task = asyncio.create_task(play_ring())
    session: ConversationSession | None = None
    recognition: Recognition | None = None

    try:
        init = json.loads(await ws.receive_text())
        if init.get("type") != "init" or not init.get("user_id") \
                or not init.get("session_id"):
            await ws.close(code=4001)
            return
        stop_ring.set()
        await ring_task

        session = ConversationSession(ws, init["user_id"], init["session_id"], storage)
        await session.say_greeting()

        recognition = Recognition(
            model=ASR_MODEL,
            format=ASR_FORMAT,
            language_hints=ASR_LANGUAGE_HINTS,
            sample_rate=ASR_SAMPLE_RATE,
            speech_noise_threshold=ASR_SPEECH_NOISE_THRESHOLD,
            callback=_AsrCallback(session),
        )
        recognition.start()

        while True:
            message = await ws.receive()
            if message.get("type") == "websocket.disconnect":
                break
            if "bytes" in message:
                recognition.send_audio_frame(message["bytes"])
            elif "text" in message:
                await session.on_text(message["text"])
    except Exception as exc:
        logger.info("voice session ended: %s", exc)
    finally:
        stop_ring.set()
        if recognition:
            try:
                recognition.stop()
            except Exception:
                pass
        if session:
            session.close()
