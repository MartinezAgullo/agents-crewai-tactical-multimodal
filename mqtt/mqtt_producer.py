#!/usr/bin/env python3
"""
MQTT Producer for Testing Tactical Agent Consumer
===============================================

This script generates test messages and publishes them to MQTT topics to test
the MQTTAgentConsumer integration with CrewAI tactical agents.

Usage:
1. Start your Mosquitto MQTT broker: podman compose up
2. Start the MQTT consumer: python mqtt/mqtt_consumer_agent.py
3. Run this producer: python mqtt/mqtt_producer.py
4. Watch the consumer process messages through tactical agents
5. Check output/ folder for generated threat analysis reports

The script sends simulated tactical alerts (alarm messages) that mimic
real-world scenarios for testing the agent processing pipeline.
"""

import sys
import os
from datetime import datetime
import json
import random
import time

# Add parent directory to path so we can import mqtt_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mqtt.mqtt_client import MQTT_Client

# Configuration
NUM_MESSAGES = 100
MIN_WAIT_SECS = 0.1
MAX_WAIT_SECS = 3
TOPIC = "Canal 1"


def generate_random_message():
    """Generate a random tactical alarm message for testing"""
    asset_id = random.randint(0, 9)
    alarm_id = random.randint(0, 5)
    timestamp = datetime.now()
    context = f"Alarm {alarm_id} in assset {asset_id}"
    
    return {
        "asset_id": asset_id,
        "alarm_id": alarm_id,
        "timestamp": timestamp.isoformat(),
        "context": context
    }


if __name__ == '__main__':
    print("MQTT Producer for Tactical Agent Testing")
    print("=" * 40)
    print(f"Topic: {TOPIC}")
    print(f"Messages to send: {NUM_MESSAGES}")
    print("Make sure MQTT broker is running and consumer is listening")
    print()
    
    # Initialize MQTT producer
    mqtt_producer = MQTT_Client(client_id="Producer")
    
    try:
        for i in range(NUM_MESSAGES):
            # Generate test message
            msg = generate_random_message()
            
            # Publish message (note: keeping original typo 'publih_message')
            mqtt_producer.publih_message(TOPIC, str(msg))
            
            print(f"Sent message {i+1}/{NUM_MESSAGES}: {msg['context']}")
            
            # Wait random interval
            time.sleep(random.uniform(MIN_WAIT_SECS, MAX_WAIT_SECS))
        
        print(f"\nCompleted sending {NUM_MESSAGES} messages")
        
    except KeyboardInterrupt:
        print("\nProducer interrupted by user")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean disconnection
        mqtt_producer.disconnect()
        print("Producer disconnected")