import asyncio
import threading
from typing import AsyncGenerator, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from config import llm_api_key, llm_base_url
from infrastructure.deidentification import filter_information

client = OpenAI(api_key=llm_api_key, base_url=llm_base_url)

def _extra_body(model: str) -> dict:
    return {"thinking": {"type": "disabled"}} if "seed" in model else {}

T = TypeVar("T", bound=BaseModel)

def _stream_sync(model: str, messages: list, temperature: float):
    for chunk in client.chat.completions.create(
        model=model,
        messages=filter_information(messages),
        stream=True,
        temperature=temperature,
        extra_body=_extra_body(model),
    ):
        try:
            delta = chunk.choices[0].delta
        except (IndexError, AttributeError):
            continue
        if delta and delta.content:
            yield delta.content

async def stream_chat(model: str, messages: list,
                      temperature: float = 0.7) -> AsyncGenerator[str, None]:
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def run() -> None:
        try:
            for delta in _stream_sync(model, messages, temperature):
                loop.call_soon_threadsafe(queue.put_nowait, delta)
        except Exception as exc:  # re-raised in the awaiting generator
            loop.call_soon_threadsafe(queue.put_nowait, exc)
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    threading.Thread(target=run, daemon=True, name="llm-stream").start()
    while True:
        item = await queue.get()
        if item is None:
            return
        if isinstance(item, Exception):
            raise item
        yield item

def complete_chat(model: str, messages: list, temperature: float = 0.7) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=filter_information(messages),
        stream=False,
        temperature=temperature,
        extra_body=_extra_body(model),
    )
    return response.choices[0].message.content or ""

def structured_completion(
    model: str,
    system: str,
    user: str,
    response_schema: Type[T],
    temperature: float = 0.0,
) -> T:
    response = client.beta.chat.completions.parse(
        model=model,
        messages=filter_information([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]),
        response_format=response_schema,
        temperature=temperature,
    )
    return response.choices[0].message.parsed
