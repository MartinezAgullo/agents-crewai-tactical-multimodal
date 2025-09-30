# MQTT Integration
[MQTT](https://mqtt.org/) consumer integration for [CrewAI](https://www.crewai.com/) tactical agents with real-time message processing capabilities.
To run the MQTT we use [Podamn](https://podman.io/) but you can use [Docker](https://www.docker.com/) intead or run Mosquitto directly wityout containers.

The follwoing instructions are to set up MQTT, a producer and a consumer with [MQTTAgentConsumer](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/mqtt/mqtt_consumer_agent.py). The `mqtt_consumer_agent.py` is just for tests, the [main code](https://github.com/MartinezAgullo/agents-crewai-tactical-multimodal/blob/main/src/main.py) incorporates its own consumer.

## Files
- `mqtt_client.py` - Base MQTT client wrapper
- `mqtt_producer.py` - Test message producer
- `mqtt_consumer_agent.py` - Agent consumer integration

## Usage with container
To test MQTT and create the flow 
```
MQTT Producer → MQTT Broker → MQTT Consumer → CrewAI Agents → Output Reports
```

1. `podman machine init`
2. `podman machine start`
3. `podman compose up` or `docker compose up` (start MQTT broker) 
4. `uv run python mqtt/mqtt_consumer_agent.py` (start consumer)  
5. `uv run python mqtt/mqtt_producer.py` (send test messages)

## Usage without containers (direct installation)
1.  **Install Mosquitto**:
```bash
   brew install mosquitto
```

2.  **Create directories and config** (from project root):
```bash
   mkdir -p mqtt/config mqtt/data mqtt/log
```

3.  **Create configuration file**:
```bash
   cat > mqtt/config/mosquitto.conf << EOF
   persistence true
   persistence_location data/
   log_dest file log/mosquitto.log
   listener 1883
   allow_anonymous true
   EOF
```

4.  **Start Mosquitto**:
```bash
   cd mqtt
   mosquitto -c config/mosquitto.conf
```

Keep this terminal open - Mosquitto runs in foreground mode


Usage
-----

### Testing the MQTT Integration

1.  **Start the consumer** (from project root):
```bash
   uv run python mqtt/mqtt_consumer_agent.py
```
2.  **Send test messages** (in another terminal):
```bash
   uv run python mqtt/mqtt_producer.py
```
3.  **Monitor output**: Check the `output/` directory for generated tactical reports