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
│   ├── data
│   ├── log
│   │   └── mosquitto.log
│   ├── mqtt_client.py
│   ├── mqtt_consumer_agent.py
│   └── mqtt_producer.py
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
        │   └── tasks.yaml
        └── tools
            ├── location_tools.py
            └── multimodal_tools.py
```
-----

### 🚀 Key Features

  * **Multimodal Input Processing**: Handles multiple input types, including images, audio, and text, by using specialized tools and an LLM with native vision capabilities.

  * **MQTT integration**: Uses and [MQTT](https://mqtt.org/) consumer to receive alerts.

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

#### Listening to MQTT messages
When executing `src/main.py`, the following queestion is asked:
```
📡 Enable MQTT consumer? (y/N):
```
If you select "y"", you should open another terminal and run  
```bash
uv run python mqtt/mqtt_producer.py
```
Then, you will see the receive and process MQTT messages through the CrewAI agents.
Notes:
 - Make sure Mosquitto is running to explore this functionality (`cd mqtt && mosquitto -c config/mosquitto.conf`)
 - The program will stay running until you press Ctrl+C
 - Both your custom input and MQTT messages get processed by the same agents
 - More info in [MQTT setup](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/mqtt/README.md)




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
### 🗺️ Geolocation Services (Example)

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
### 📡  OpenTelemetry
Can be use with container or standalone.

**Use with Podman**
(Podman didn't work for me)

1. Step 1: Install Podman
```bash
# Install 
brew install podman podman-compose

# Initialize and start Podman machine
podman machine init
podman machine start
```

2. Step 2: Create OpenObserve Configuration
```bash
# From your project root
mkdir -p openobserve
cd openobserve
```
Create the Create `docker-compose.yaml`.

3. Step 3: Start OpenObserve
```bash
# From the openobserve/ directory
podman-compose up -d

# Check if it's running
podman-compose ps

# View logs (optional)
podman-compose logs -f
```
**Standalone use**
1. [Dowload](https://openobserve.ai/downloads/) the binary 
```
curl -L -o openobserve-ee-v0.15.1-darwin-arm64.tar.gz https://downloads.openobserve.ai/releases/o2-enterprise/v0.15.1/openobserve-ee-v0.15.1-darwin-arm64.tar.gz
tar -zxvf openobserve-ee-v0.15.1-darwin-arm64.tar.gz
```
2. Start OpenObserve
```bash
cd ~/openobserve
export ZO_ROOT_USER_EMAIL="root@example.com"
export ZO_ROOT_USER_PASSWORD="Complexpass#123"
export ZO_DATA_DIR="./data"
./openobserve
```
Keep this terminal open.

3. Verify OpenObserve is Running

In a new terminal:
```bash
curl http://localhost:5080/healthz
```
Should return: `{"status":"ok"}`


4. Run the Project

``` bash
uv run python src/main.py
```

5. . View Traces

Open <http://localhost:5080> in browser:

-   Navigate to [Traces](http://localhost:5080/web/traces)
-   Select stream: **default**
-   View agent executions, LLM calls, and performance metrics

**Getting the Authorization Header**

1. Open http://localhost:5080 and log in
2. Navigate to: **Ingesta → Personalizado → Registros → Otel Collector**
3. Copy the `Authorization` header value from the curl example shown
4. Add to your `.env` file:
```bash
   OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <your-copied-value>"
```

-----
### 📺 Gradio interface
A Gradio interface has been incorported via the [TacticalAnalysisInterface](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/gradio_interface.py).
    <figure style="margin: 0;">
        <img src="https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/output/GradioInterface.png" alt="Gradio interface" style="width: 100%; max-width: 400px; display: block;">
        <figcaption style="text-align: center; font-size: 0.9em; color: #555;">
            Gradio interface
        </figcaption>
    </figure>

