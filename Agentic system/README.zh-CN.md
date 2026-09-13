## 目录结构

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

## 文件说明

### 入口与配置

| 文件 | 作用 |
|---|---|
| `main.py` | 程序入口。 |
| `config.py` | 集中配置：模型角色、语音参数、路径与对话推进节奏。 |
| `requirements.txt` | Python 依赖。 |
| `server_key_example` | 本地 `server_key` 文件的模板，用于存放 API 密钥。 |

### dialogue_orchestrator/

| 文件 | 作用 |
|---|---|
| `dialogue_orchestrator.py` | 管理对话流程与状态流转。 |
| `advice_communicator.py` | 在适当阶段向对话参与者传递个性化建议。 |
| `dialogue_voice.py` | `/ws` 上的双工语音会话：语音输入与语音输出。 |

### dialogue_monitor/

| 文件 | 作用 |
|---|---|
| `dialogue_monitor_agent.py` | 监测对话，并依据对对话的评估触发相应评估流程。 |
| `dimensions.py` | 监测维度。 |

### risk_assessment/

| 文件 | 作用 |
|---|---|
| `risk_assessment_agent.py` | 在指定的健康维度上开展健康风险评估。 |

### personalization_engine/

| 文件 | 作用 |
|---|---|
| `dialogue_adaption.py` | 结合用户背景与对话上下文，生成贴合情境的回应。 |
| `context_retriever.py` | 检索对话参与者的上下文。 |
| `advice_agent.py` | 依据评估结果与用户上下文生成个性化建议。 |
| `user_profile.py` | 管理参与者资料，并将一次已结束的会话压缩为记忆摘要。 |
| `auxiliary.py` | 训练推荐相关的支撑函数。 |

### coping_skills_training/

| 文件 | 作用 |
|---|---|
| `coping_skills_training.py` | 训练 agent。依据聊天记录与过往训练表现触发。 |
| `training_interaction.py` | 训练交互接口。 |

### safety/

| 文件 | 作用 |
|---|---|
| `crisis_watcher.py` | 运行危机判定，并推送界面展示的预警。 |

**说明**：本仓库只实现了危机检测；文章中的幻觉检测环节未包含在本演示中。

### infrastructure/

| 文件 | 作用 |
|---|---|
| `model_gateway.py` | 所有 agent 调用模型提供方的唯一通路，用于统一控制去标识化与不阻塞事件循环的流式输出。 |
| `deidentification.py` | 去除可识别个人身份的信息。 |
| `message_protocol.py` | 消息结构、前端事件契约，以及同一会话的多种视图。 |
| `session_store.py` | 基于文件的 JSON 持久化：用户、会话、记忆与解锁码。 |
| `concurrency_locks.py` | 会话级与用户级锁，避免两个标签页之间相互覆盖。 |

### user_interaction/

Vue 3 单页应用（由 Vite 构建），其产物由 `main.py` 从 `dist/` 目录提供。

| 文件 | 作用 |
|---|---|
| `src/views/Chat.vue` | 对话界面：流式回复、评分滑杆，以及驱动它们的整个流程。 |
| `src/components/ChatMessage.vue` | 单条气泡，以及该消息 `events` 所要求的交互步骤（领域选择、计划卡片、训练卡片、反思选择）。 |
| `src/components/VoiceCall.vue` | 语音浮层：麦克风采集、实时字幕与打断。 |
| `src/components/CrisisWatcher.vue` | 保持 `/ws2` 连接，收到预警时弹出安全提示卡片。 |
| `src/utils/api.js` | 接口调用与前端响应的事件名。 |

### prompts/

| 文件 | 作用 |
|---|---|
| `shared.py` | 各 agent 共用的提示词文本。 |
| `dialogue_orchestrator.py` | 对话编排器的提示词。 |
| `dialogue_monitor.py` | 对话监测器的提示词。 |
| `risk_assessment.py` | 风险评估 agent 的提示词。 |
| `personalization_engine.py` | 个性化引擎的提示词。 |
| `coping_skills_training.py` | 训练 agent 的提示词。 |
| `safety.py` | 危机判定与预警文案的提示词。 |

**说明**：这些提示词是为本演示撰写的，并非生产环境提示词的翻译。真实试验所使用的提示词以中文撰写，并经过文章所述社区共同设计流程打磨。

## 快速开始

### 1. 安装后端依赖

需要 **Python 3.10+**。

```bash
pip install -r requirements.txt
```

### 2. 配置密钥

```bash
cp server_key_example server_key
```

`server_key` 中每行填写一项 `KEY=value`。`LLM_API_KEY` 为必填项，任何兼容 OpenAI 协议的 chat-completions 服务均可使用；`LLM_BASE_URL` 用于指定服务地址。仅在使用语音功能时需要 `DASHSCOPE_API_KEY`。该文件已被 gitignore，请勿将真实密钥提交至仓库。

### 3. 配置模型

`config.py` 中为每个 agent 角色配置一个模型：`MODEL_DIALOGUE`、`MODEL_MONITOR`、`MODEL_ASSESSMENT`、`MODEL_ADVICE`、`MODEL_SAFETY`。多个角色可共用同一模型，也可分别指定。`ASR_*` / `TTS_*` 用于配置语音服务的地址与音色；未配置语音密钥时，除 `/ws` 之外的功能均可正常使用。

### 4. 构建前端

```bash
cd user_interaction
npm install
npm run build
```

### 5. 运行

```bash
python main.py                 # http://127.0.0.1:9214
```

前端开发时，可运行 `npm run dev`：页面由 Vite 在 :5173 提供，API 请求自动代理至 :9214。

## 伦理声明

- 本项目为**研究原型，仅用于演示**。它不是医疗器械，不提供诊断、治疗或专业心理卫生照护，也**不能替代专业帮助**。如您正处于困扰或危机之中，请立即联系专业人员或当地紧急服务。

- `safety/` 模块是演示，不是一套可靠的安全防护体系；去标识化基于规则实现，同样不构成保证。二者在真实部署前都需要经过验证、人工复核并明确责任归属。

- 演示数据均保存在本机。**请勿使用真实个人数据运行本演示**。真实世界随机对照试验中收集的数据，受文章所述知情同意与隐私框架约束。
