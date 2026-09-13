## Directory Structure

```
System demonstration
│
├── main.py
│
├── config.py
│
├── requirements.txt
│
├── server_key_example
│
├── api
│   ├── account.py
│   ├── conversation.py
│   ├── dependencies.py
│   └── realtime.py
│
├── dialogue_orchestrator
│   ├── dialogue_orchestrator.py
│   ├── advice_communicator.py
│   └── dialogue_voice.py
│
├── dialogue_monitor
│   ├── dialogue_monitor_agent.py
│   └── dimensions.py
│
├── risk_assessment
│   └── risk_assessment_agent.py
│
├── personalization_engine
│   ├── dialogue_adaption.py
│   ├── context_retriever.py
│   ├── advice_agent.py
│   ├── user_profile.py
│   └── auxiliary.py
│
├── coping_skills_training
│   ├── coping_skills_training.py
│   └── training_interaction.py
│
├── safety
│   └── crisis_watcher.py
│
├── infrastructure
│   ├── model_gateway.py
│   ├── deidentification.py
│   ├── message_protocol.py
│   ├── session_store.py
│   └── concurrency_locks.py
│
├── prompts
│   ├── shared.py
│   ├── dialogue_orchestrator.py
│   ├── dialogue_monitor.py
│   ├── risk_assessment.py
│   ├── personalization_engine.py
│   ├── coping_skills_training.py
│   └── safety.py
│
└── user_interaction
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── public/companion.svg
    └── src/
```

## File Descriptions

### Entry point and configuration

| File | Role |
|---|---|
| `main.py` | Application entry point. |
| `config.py` | Central configuration: model roles, speech settings, paths, conversation pacing. |
| `requirements.txt` | Python package dependencies. |
| `server_key_example` | Template for the local `server_key` file that holds the API keys. |

### dialogue_orchestrator/

| File | Role |
|---|---|
| `dialogue_orchestrator.py` | Manages the conversation flow and state transitions. |
| `advice_communicator.py` | Delivers tailored advice to the chat participant at the appropriate stage. |
| `dialogue_voice.py` | The duplex voice session over `/ws`: speech in and speech out. |

### dialogue_monitor/

| File | Role |
|---|---|
| `dialogue_monitor_agent.py` | Monitors the conversation and triggers an assessment based on its evaluation of the dialogue. |
| `dimensions.py` | Monitor dimensions. |

### risk_assessment/

| File | Role |
|---|---|
| `risk_assessment_agent.py` | Conducts health risk assessment across the designated health domains. |

### personalization_engine/

| File | Role |
|---|---|
| `dialogue_adaption.py` | Shapes context-aware responses to match the user's background and conversation context. |
| `context_retriever.py` | Retrieves chat participants' context. |
| `advice_agent.py` | Generates personalized advice based on assessment results and user context. |
| `user_profile.py` | Manages the participant's profile and compresses a finished session into a memory digest. |
| `auxiliary.py` | Supporting functions for training recommendation. |

### coping_skills_training/

| File | Role |
|---|---|
| `coping_skills_training.py` | The training agents. They activate based on chat history and past training performance. |
| `training_interaction.py` | The training interface. |

### safety/

| File | Role |
|---|---|
| `crisis_watcher.py` | Runs the crisis verdict and pushes the alert the interface shows. |

**Note:** this repo implements the crisis-detection only; the hallucination-detection stages from the article are not included in this demo. 

### infrastructure/

| File | Role |
|---|---|
| `model_gateway.py` | The single path every agent uses to call the model provider for controlling de-identification and off-loop streaming. |
| `deidentification.py` | Removes personally identifiable information. |
| `message_protocol.py` | The message structure, the UI event contract, and the views over a session. |
| `session_store.py` | File-backed JSON persistence for users, sessions, memories, and unlock codes. |
| `concurrency_locks.py` | Per-session and per-user locks, so two tabs cannot overwrite each other. |

### user_interaction/

A Vue 3 single-page app (Vite), served by `main.py` from `dist/`.

| File | Role |
|---|---|
| `src/views/Chat.vue` | The conversation screen: streaming replies, the rating slider, and the flow that drives them. |
| `src/components/ChatMessage.vue` | A bubble, plus the interactive step its `events` ask for (domain picker, plan card, training card, reflection). |
| `src/components/VoiceCall.vue` | The voice overlay: microphone capture, live captions, barge-in. |
| `src/components/CrisisWatcher.vue` | Holds `/ws2` open and shows the safety card when an alert arrives. |
| `src/utils/api.js` | The API calls and the event names the interface reacts to. |

### prompts/
| File | Role |
|---|---|
| `shared.py` | Prompt text shared across agents. |
| `dialogue_orchestrator.py` | Prompts for the dialogue orchestrator. |
| `dialogue_monitor.py` | Prompts for the dialogue monitor. |
| `risk_assessment.py` | Prompts for the risk-assessment agent. |
| `personalization_engine.py` | Prompts for the personalization engine. |
| `coping_skills_training.py` | Prompts for the training agents. |
| `safety.py` | Prompts for the crisis verdict and the alert copy. |

**Note:** these prompts were written for this demo, not translated from
production. The trial prompts were written in Chinese, through the community
codesign process described in the Article.


## Demo Quick Start

### 1. Install the backend

Requires **Python 3.10+**.

```bash
pip install -r requirements.txt
```

### 2. Configure the keys

```bash
cp server_key_example server_key
```

Fill in `server_key`, one `KEY=value` per line. `LLM_API_KEY` is required; any OpenAI-compatible chat-completions endpoint works. `LLM_BASE_URL` points at it. `DASHSCOPE_API_KEY` is only needed for voice. The file is gitignored, so don't commit real keys.

### 3. Configure the models

`config.py` has one model per agent role: `MODEL_DIALOGUE`, `MODEL_MONITOR`, `MODEL_ASSESSMENT`, `MODEL_ADVICE`, `MODEL_SAFETY`. Share one model across roles or give each its own. `ASR_*` / `TTS_*` set the speech endpoints and voices; without a speech key everything but `/ws` still works.

### 4. Build the interface

```bash
cd user_interaction
npm install
npm run build
```

### 5. Run

```bash
python main.py                 # http://127.0.0.1:9214
```

To work on the interface, `npm run dev` serves it on :5173 and proxies the API to :9214.

## Ethics Statement

- This is a **research prototype, for demonstration only**. It is not a
  medical device. It does not diagnose, treat, or provide professional mental health care.
  The system is **not a substitute for professional help**. Individuals in distress or crisis
  should immediately seek support from qualified professionals or local emergency services.

- The safety/ module is a demonstration, not a safeguarding system, and de-identification is rule-based,
  not a guarantee — both need real validation, human review, and accountability before any real deployment.

- Demo data is stored locally on your machine. **Do not run this demo with real personal data**.
  Data collected in the real-world RCT is governed by the informed-consent and privacy framework described in the Article.

