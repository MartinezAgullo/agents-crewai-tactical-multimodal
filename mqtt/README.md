# MQTT Integration
MQTT consumer integration for CrewAI tactical agents with real-time message processing capabilities.
To run the MQTT we use Podamn but you can use Docker intead or run Mosquitto directly wityout containers.

## Files
- `mqtt_client.py` - Base MQTT client wrapper
- `mqtt_producer.py` - Test message producer
- `mqtt_consumer_agent.py` - Agent consumer integration

## Usage 
To test MQTT and create the flow 
```
MQTT Producer → MQTT Broker → MQTT Consumer → CrewAI Agents → Output Reports
```

1. `podman machine init`
2. `podman machine start`
3. `podman compose up` (start MQTT broker) // youcould do `docker compose up`
4. `uv run python mqtt/mqtt_consumer_agent.py` (start consumer)  
5. `uv run python mqtt/mqtt_producer.py` (send test messages)