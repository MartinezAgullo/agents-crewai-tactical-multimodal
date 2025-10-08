# agents-crewai-tactical-multimodal

## A Multimodal AI Agent Crew for Tactical Analysis

This project showcases a multi-agent system built with the [**CrewAI**](https://www.crewai.com/) framework, designed to simulate a tactical military analysis pipeline. It is capable of processing diverse inputs—including text reports, images, and audio files to provide real-world threat assessments. 

-----

### ⚙️ Core Functionality

The system operates a specialized crew of AI [agents](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/tactical/config/agents.yaml) that perform the following steps:

1.  **Threat Analysis:** The **Threat Analyst Agent** identifies hostile entities from raw inputs. It leverages multimodal capabilities to process images and audio, and custom tools to get real-time geographic context.
2.  **Report Generation:** The **Report Generator Agent** synthesizes the analysis into a professional, concise situation report.
3.  **Tactical Response:** The **Tactical Advisor Agent** suggests a strategic and well-reasoned response to the identified threats.

Design pattern: These agents are connected by a **prompt chaining workflow**. This means that the general task is decomposed into a sequence of steps in which each LLM call processes the output of the precious one. The main goal is to trade off latency for higher accuracy, by making each LLM call an easier task.

The final output for each step is saved in markdown format to the `output/` directory.

-----
### 📁 Project Structure
This project follows the standard CrewAI scafolding

```
.
├── gradio_interface.py
├── mqtt
│   ├── config
│   │   └── mosquitto.conf
│   ├── log
│   │   └── mosquitto.log
│   ├── mqtt_client.py
│   ├── mqtt_consumer_agent.py
│   └── mqtt_producer.py
├── openobserve
│   └── openobserve
├── output
│   ├── GradioInterface.png
│   ├── report_generation_task.md
│   ├── tactical_response_task.md
│   └── threat_analysis_task.md
├── pyproject.toml
└── src
    ├── crew.py
    ├── llm_manager.py
    ├── main.py
    └── tactical
        ├── config
        │   ├── agents.yaml
        │   ├── classifications.yaml
        │   ├── execution_config.yaml
        │   └── tasks.yaml
        ├── references
        │   └── insignia
        └── tools
            ├── classification_tool.py
            ├── location_tools.py
            └── multimodal_tools.py
```
-----

### 🚀 Key Features

  * **Multimodal Input Processing**: Handles multiple input types, including images, audio, and text, by using specialized tools and an LLM with native vision capabilities.
      - The audio is processed using [whisper](https://openai.com/index/whisper/) and [pyannote](https://huggingface.co/pyannote).
      <!-- The audio has been created with [ElevenLabs](https://elevenlabs.io/app/speech-synthesis/text-to-speech) -->


  * **MQTT integration**: Uses an [MQTT](https://mqtt.org/) consumer to receive alerts.

  * **OpenObserve**: Uses [OpenObserve](https://openobserve.ai/) for telemetry monitoring.

  * **Dynamic Geolocation**: Automatically retrieves the current location via IP address or accepts a specific location from the user to provide real-world tactical context. 

  * **Robust LLM Fallback System**: A custom `LLMManager` handles a hierarchy of LLMs, ensuring the best-suited model is chosen for each [task](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/tactical/config/tasks.yaml) (e.g., a "reasoning" model for analysis, a "flash" model for quick tasks), with fallback options to ensure reliability.

  * **Modular Architecture**: The project is structured with the traditional CrewAI style, i.e. separate configuration files (`.yaml`) for [agents](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/tactical/config/agents.yaml) and [tasks](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/tactical/config/tasks.yaml), making it easy to configure and extend. The custom tools can be defined using BaseTool from crewai.tools.

-----

### 🛠️ Setup and Installation

Follow these steps to get the project up and running.

1.  **Prerequisites**: Ensure you have **Python 3.11.9** installed. This project uses `uv`, a fast Python package installer and dependency manager.

2.  **API Keys**: Create a `.env` file in the root directory and add your API keys for the LLMs you want to use. This project is configured to support multiple providers for robust fallback.

    ```
    OPENAI_API_KEY=your_key_here
    ANTHROPIC_API_KEY=your_key_here
    GOOGLE_API_KEY=your_key_here
    ...
    ```

3.  **Install Dependencies**: Use `uv` to create a virtual environment and install the required packages from `pyproject.toml`.

    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install
    ```

-----

### 🏃 How to Run

To start the tactical analysis crew, execute the following command from the root directory:

```bash
uv run python src/main.py
```

The terminal will provide a detailed log of the agents' thought processes, and the final reports will be saved in the `output/` directory.

You can modify the mission input and location in src/main.py to test different scenarios.:
 - mission_input: Point to text, image or audio file or directly write some mission report.
 - location_input: Provide name or coordinates. If location_input=None, your IP location will be used.

For users who prefer a graphical interface, do:
```bash
uv run python gradio_interface.py
```

#### Configuration:

Edit the configuration file `execution_config.yaml` in order to disable or enable the different services.
```bash
vim src/tactical/config/execution_config.yaml
```
From here you can control wether or not to use the enhance LLM manager, the consumtion of MQTT messages and the open telemetry monitoring. 
```bash
execute_LLM_manager: false
enable_MQTT_consumer: false
enable_telemetry: false
```

**MQTT**
If you set enable_MQTT_consumer to true, in a separete terminal you shall execute the command below to prouce messages:
```bash
uv run python mqtt/mqtt_producer.py
```
Then, you will see the receive and process MQTT messages through the CrewAI agents.
Notes:
 - Make sure Mosquitto is running to explore this functionality (`cd mqtt && mosquitto -c config/mosquitto.conf`)
 - The program will stay running until you press Ctrl+C
 - Both your custom input and MQTT messages get processed by the same agents
 - More info in [MQTT setup](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/mqtt/README.md)


**Recording traces**
If you set enable_telemetry to true, read the **OpenTelemetry Setup** section below.

-----

### 📚 LLM manager
The LLM-fallback-manager system performs an acutual API call during its initizalisation. This goes beyond a simple check of envirorment variables.
The system tests each configured model to confirm that it's not only set up correctly but is also functional and responsive.

Example output of the LLM manager:

```bash
======================================================================
🤖 LLM CONFIGURATION STATUS (EXPANDED MODELS)
======================================================================

 Reasoning models :: Tactical analysis & strategy
  Reasoning Model A    ✅ gpt-4-turbo
  Reasoning Model B    ❌ claude-3-5-sonnet-20241022 not configured
  Reasoning Model C    ❌ gemini-2.0-flash-exp not configured
  Reasoning Model D    ✅ gpt-4
  Reasoning Model E    ❌ mistral-large-2411 not configured
  Reasoning Model F    ❌ deepseek-r1-distill-llama-70b not configured
  Reasoning Model G    ❌ qwen/qwen-2.5-72b-instruct not configured
  Reasoning Model H    ✅ llama-3.3-70b-versatile

 Flash models :: Fast responses & editing
  Flash Model A        ✅ llama-3.3-70b-versatile
  Flash Model B        ✅ llama-3.1-8b-instant
  Flash Model C        ❌ gemini-2.0-flash-exp not configured
  Flash Model D        ✅ gpt-4o-mini
  Flash Model E        ✅ gpt-3.5-turbo
  Flash Model F        ✅ claude-3-haiku-20240307
  Flash Model G        ❌ mistral-small-2409 not configured

 Multimodal models :: Vision & complex input
  Multimodal Model A   ✅ gpt-4o
  Multimodal Model B   ❌ gemini-2.0-flash-exp not configured
  Multimodal Model C   ✅ gpt-4-turbo
  Multimodal Model D   ✅ gpt-4
  Multimodal Model E   ❌ claude-3-5-sonnet-20241022 not configured
  Multimodal Model F   ✅ gpt-4o-mini

  Fallback model :: Emergency backup
  Fallback Model      ✅ gpt-3.5-turbo

📊 SUMMARY
  Total WORKING Models: 13
  Reasoning: 3/8
  Flash: 5/7
  Multimodal: 4/6
  Fallback: 1/1

✅ SUCCESS: 13 models are working and ready!
   You have excellent model diversity!
```
### 🗂️ Classification System

The system uses a rule-based classification tool to identify entities as **Friend**, **Foe**, **Civilian**, or **Unknown**.

#### How It Works

1\. For each entity detected by `threat_analyst_agent`, the agent calls the [Classification Reference Tool](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/classification_tool.py)

2\. The tool loads the defined criteria from `classifications.yaml` including:

   - Uniform patterns and insignia descriptions

   - Behavioral indicators

   - Decision process rules

3\. Agent compares observed characteristics against criteria

4\. Entity is classified based on definitive matches:

   - **Friend**: NATO/UN/Ally insignia + military uniform

   - **Foe**: Hostile insignia + military organization

   - **Civilian**: No uniform + unarmed + non-threatening

   - **Unknown**: Armed civilians, mixed indicators, or insufficient data


**No guessing**: If classification is ambiguous, the entity is marked as Unknown with explanation. Accuracy is prioritized over speed to prevent operational errors.

#### Configuration

- Classification rules and criteria: `src/tactical/config/classifications.yaml`

- Reference images: `src/tactical/references/insignia/`


### 🗺️ Geolocation Services

The system's `LocationContextTool` can be used to add geographic context to the mission. Here's how to configure it in `src/main.py`:

```python
# Option 1: Auto-detect location via IP
current_location = None

# Option 2: Specify a location by name
# current_location = "Valencia, Spain"

# Option 3: Specify coordinates
# current_location = "40.4168, -3.7038" # Madrid coordinates
```

  * **Note:** The agent is designed to use this tool autonomously as part of its task, so you only need to set the `current_location` variable.

-----
### 📡 OpenTelemetry Setup
This project supports telemetry monitoring using [OpenObserve](https://openobserve.ai/). You can run OpenObserve either with containers (Podman/Docker) or as a standalone binary.

OpenObserve can be deployed in two ways:
1. **Standalone binary** (recommended for macOS): A single executable that runs directly on your machine - simpler setup, no container dependencies
2. **Container deployment** (Podman/Docker): Isolated environment with automatic restarts and easier management - better for production use. 

The telemetry system is completely **optional** and can be toggled on/off via environment variables without modifying your code. When disabled, your project runs normally with zero performance overhead.

#### Option 1: Standalone Binary (Recommended for macOS)

1. [Dowload](https://openobserve.ai/downloads/) the binary 
```bash
cd ~
mkdir openobserve && cd openobserve
curl -L -o openobserve-ee-v0.15.1-darwin-arm64.tar.gz https://downloads.openobserve.ai/releases/o2-enterprise/v0.15.1/openobserve-ee-v0.15.1-darwin-arm64.tar.gz
tar -zxvf openobserve-ee-v0.15.1-darwin-arm64.tar.gz
```
For other platforms, visit: https://github.com/openobserve/openobserve/releases

2. Start OpenObserve
```bash
cd ~/openobserve
export ZO_ROOT_USER_EMAIL="root@example.com"
export ZO_ROOT_USER_PASSWORD="Complexpass#123"
export ZO_DATA_DIR="./data"
./openobserve
```
⚠️ Keep this terminal open - OpenObserve runs in the foreground.

3. Verify OpenObserve is Running

In a new terminal:
```bash
curl http://localhost:5080/healthz
```
Should return: `{"status":"ok"}`

#### Option 2: Using Podman/Docker
(Podman didn't work for me)

1. Install Podman
```bash
# Install 
brew install podman podman-compose

# Initialize and start Podman machine
podman machine init
podman machine start
```

2. Create OpenObserve Configuration
```bash
# From your project root
mkdir -p openobserve
cd openobserve
```
Create the Create `docker-compose.yaml`.

3. Start OpenObserve
```bash
# From the openobserve/ directory
podman-compose up -d

# Check if it's running
podman-compose ps

# View logs (optional)
podman-compose logs -f
```

**Getting the Authorization Header**

1. Open http://localhost:5080 and log in
2. Navigate to: **Ingesta → Personalizado → Registros → Otel Collector**
3. Copy the `Authorization` header value from the curl example shown
4. Add to your `.env` file:
```bash
   OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <your-copied-value>"
```

**Run and Monitor**
1. Run the Project:
``` bash
uv run python src/main.py
```

2. View Traces
- Open <http://localhost:5080> in browser:
- Navigate to [Traces](http://localhost:5080/web/traces)
- Select stream: **default**
- View agent executions, LLM calls, and performance metrics

**Stop OpenObserve**
A) Standalone
``` bash
# Press Ctrl+C in the OpenObserve terminal
```
B) Podman
``` bash
podman-compose down
```

-----
### 📺 Gradio interface
An alternative web-based interface is available via Gradio for users who prefer a graphical interface over the command line.
It has been incorported via the [TacticalAnalysisInterface](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/gradio_interface.py).
    <figure style="margin: 0;">
        <img src="https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/output/GradioInterface.png" alt="Gradio interface" style="width: 100%; max-width: 400px; display: block;">
    </figure>

#### Launch Gradio Interface

**Instead of running `main.py`**, launch the Gradio interface:
```bash
uv run python gradio_interface.py
```

Note I: Gradio interface provides the same tactical analysis capabilities as main.py but through an interactive web UI. Use either the Gradio interface OR the command-line execution, not both simultaneously.

Note II: Neither MQTT nor OpenObserve have been implemented on gradio yet.





<!-- tree -I "__pycache__|agents_crewai_tactical_multimodal.egg-info|__init__.py|inputs|uv.lock|README.md|data|openobserve-ee-v0.15.1-darwin-arm64.tar.gz" -->