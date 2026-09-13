"""Configuration for the demo.

Credentials are read from environment variables, then from a local
`server_key` file. No secret is stored in this repository.
"""

import os

project_root = os.path.dirname(os.path.abspath(__file__))


def _credential(name: str) -> str:
    value = os.environ.get(name, "")
    if value:
        return value
    path = os.path.join(project_root, "server_key")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() == name:
                return val.strip()
    return ""

llm_api_key = _credential("LLM_API_KEY")
llm_base_url = _credential("LLM_BASE_URL")
dashscope_api_key = _credential("DASHSCOPE_API_KEY")

if not llm_api_key:
    raise RuntimeError(
        "Missing LLM credentials. Copy `server_key_example` to `server_key` "
        "and fill in LLM_API_KEY (and LLM_BASE_URL for a non-default "
        "endpoint), or set the environment variables of the same names."
    )


# Replace these placeholders with the models your deployment uses.
MODEL_DIALOGUE = "your-model"
MODEL_MONITOR = "your-model"
MODEL_ASSESSMENT = "your-model"
MODEL_ADVICE = "your-model"
MODEL_SAFETY = "your-model"

# Voice mode is optional. Replace these endpoints and model names as needed.
ASR_ENDPOINT = "wss://your-realtime-asr.example.com"
TTS_ENDPOINT = "wss://your-realtime-tts.example.com"

ASR_MODEL = "your-asr-model"
ASR_FORMAT = "pcm"
ASR_SAMPLE_RATE = 16000
ASR_LANGUAGE_HINTS = ["en", "zh"]
ASR_SPEECH_NOISE_THRESHOLD = 0.3

TTS_MODEL = "your-tts-model"
TTS_VOICE = "your-voice"

data_dir = os.path.join(project_root, "data")
web_dir = os.path.join(project_root, "user_interaction", "dist")

# Conversation pacing
REPORT_CHECK_START = 10
ADVICE_CHECK_START = 8
POST_REPORT_ADVICE_TURNS = 10
HARD_MAX_TURNS = 40
