#!/usr/bin/env python3
"""
MQTT Agent Consumer Test Script
===============================

This script is used to test the MQTT consumer integration with CrewAI tactical agents
before integrating it with the Gradio interface or main.py application.

Usage:
1. Start your Mosquitto MQTT broker: podman compose up
2. Run this script: python mqtt_consumer_agent.py
3. Send test messages using your mqtt_producer.py
4. Verify that agents process the messages and generate outputs in the output/ folder

The script will block the terminal while consuming messages. Use Ctrl+C to stop.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mqtt.mqtt_client import MQTT_Client
from src.crew import TacticalCrew


class MQTTAgentConsumer:
    """Simple MQTT consumer that processes messages through CrewAI tactical agents"""
    
    def __init__(self, topics=["Canal 1"], crew_instance=None):
        """
        Initialize MQTT consumer for agent processing
        
        Args:
            topics: List of MQTT topics to subscribe to
            crew_instance: TacticalCrew instance (creates new one if None)
        """
        self.topics = topics if isinstance(topics, list) else [topics]
        self.crew_instance = crew_instance or TacticalCrew()
        self.mqtt_client = None
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            print("Connected to MQTT broker successfully")
            # Subscribe to all specified topics
            for topic in self.topics:
                client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        else:
            print(f"Connection failed with code: {rc}")

    def on_message(self, client, userdata, msg):
        """Callback for received MQTT messages - processes through agents"""
        print(f"\nReceived MQTT message on topic '{msg.topic}': {msg.payload.decode()}")
        
        # Convert MQTT message to tactical input format
        mission_input = f"MQTT Alert from {msg.topic}: {msg.payload.decode()}"
        
        # Process the message through the tactical crew
        try:
            print("Processing message through tactical agents...")
            
            inputs = {
                'mission_input': mission_input,
                'location_input': None  # Auto-detect location via IP
            }
            
            result = self.crew_instance.crew().kickoff(inputs=inputs)
            
            print("Agent processing completed successfully!")
            print("Check the output/ folder for generated reports")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error processing message with agents: {e}")

    def start(self):
        """Start consuming MQTT messages"""
        print("Initializing MQTT Agent Consumer...")
        
        self.mqtt_client = MQTT_Client(
            client_id="AgentConsumer",
            on_connect=self.on_connect,
            on_message=self.on_message
        )
        
        print("Starting MQTT consumer (blocking mode)...")
        print("Press Ctrl+C to stop")
        
        try:
            # This will block until interrupted
            self.mqtt_client.client.loop_forever()
        except KeyboardInterrupt:
            print("\nStopping MQTT consumer...")
            self.stop()

    def stop(self):
        """Stop the MQTT consumer"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            print("MQTT consumer disconnected")


if __name__ == '__main__':
    # Test configuration
    test_topics = ["Canal 1", "alerts"]  # Add your test topics here
    
    print("MQTT Agent Consumer Test")
    print("=" * 30)
    print(f"Topics to monitor: {test_topics}")
    print("Make sure your MQTT broker is running (podman compose up)")
    print()
    
    # Create and start consumer
    consumer = MQTTAgentConsumer(topics=test_topics)
    consumer.start()