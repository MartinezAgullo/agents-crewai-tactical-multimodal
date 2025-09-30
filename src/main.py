import sys
import warnings
import threading
import os
import logging
from crew import TacticalCrew, test_enhanced_llm_connectivity


# Check if telemetry is enabled (CrewAI handles .env loading automatically)
logging.getLogger("openlit").setLevel(logging.WARNING)
TELEMETRY_ENABLED = os.getenv('TELEMETRY_ENABLED', 'false').lower() in ['true', '1', 'yes', 'on']

if TELEMETRY_ENABLED:
    print("📊 Telemetry ENABLED - Initializing instrumentation...")
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        import openlit

        # Configure provider
        provider = TracerProvider()
        exporter = OTLPSpanExporter() 
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        
        # Instrument CrewAI and OpenAI
        CrewAIInstrumentor().instrument()
        OpenAIInstrumentor().instrument()
        
        # Token monitoring
        openlit.init()
        
        print("✅ Telemetry initialized successfully")
        print(f"   📡 Endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')}")
        print(f"   🏷️  Service: {os.getenv('OTEL_SERVICE_NAME')}")
        
    except Exception as e:
        print(f"❌ Failed to initialize telemetry: {e}")
        print("   Continuing without telemetry...")
        TELEMETRY_ENABLED = False
else:
    print("ℹ️  Telemetry DISABLED (set TELEMETRY_ENABLED=true in .env to enable)")



warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Runs the Tactical Crew mission with a hardcoded mission report.
    This structure is modular and includes robust error handling.
    """
    
    print("\n" + "="*60)
    print("🔧 INITIALIZING TACTICAL CREW SYSTEM")
    print("="*60)
    
    # Test LLM connectivity first
    print("🧪 Step 1: Testing Enhanced LLM connectivity...")
    connectivity_ok = test_enhanced_llm_connectivity()
    
    if not connectivity_ok:
        print("❌ LLM connectivity test failed!")
        sys.exit(1)
    
    print("✅ LLM connectivity test passed!")
    
    #mission_input = "inputs/text_inputs/mission_report_01.txt"
    mission_input = "inputs/image_inputs/test_image_11_mediterranean_drone.png"

    location_input= None
    

    inputs = {
        'mission_input': f"{mission_input}",
        'location_input': f"{location_input}"
    }
    
    try:
        print("\n🚀 Step 2: Initializing Tactical Crew...")
        print("="*60)
        
        # Create an instance of the TacticalCrew
        crew_instance = TacticalCrew()

        # MQTT Integration - Optional
        mqtt_enabled = input("\n📡 Enable MQTT consumer? (y/N): ").lower().strip() == 'y'
        
        if mqtt_enabled:
            print("🔗 Starting MQTT consumer...")
            mqtt_thread = start_mqtt_consumer(crew_instance)
            print("✅ MQTT consumer started in background")

        
        print("\n🎯 Step 3: Starting Mission Analysis...")
        print("="*60)
        
        # Get the crew object and run the mission
        result = crew_instance.crew().kickoff(inputs=inputs)

        print("\n" + "="*60)
        print("🎖️  TACTICAL ANALYSIS MISSION COMPLETE")
        print("="*60)
        print(result)
        
        print("\n✅ Mission completed successfully!")

        if mqtt_enabled:
            print("📡 MQTT consumer continues running in background...")
            print("Press Ctrl+C to stop everything")
            
            # Keep main thread alive if MQTT is running
            try:
                mqtt_thread.join()
            except KeyboardInterrupt:
                print("\n🛑 Stopping MQTT consumer...")

    except Exception as e:
        print(f"\n❌ An error occurred while running the crew: {e}", file=sys.stderr)
        sys.exit(1)

def start_mqtt_consumer(crew_instance):
    """Start MQTT consumer in background thread"""
    try:
        mqtt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mqtt')
        if mqtt_path not in sys.path:
            sys.path.insert(0, mqtt_path)
        from mqtt.mqtt_consumer_agent import MQTTAgentConsumer
        
        def run_mqtt():
            consumer = MQTTAgentConsumer(
                topics=["Canal 1", "alerts"],
                crew_instance=crew_instance
            )
            consumer.start()
        
        mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
        mqtt_thread.start()
        return mqtt_thread
        
    except ImportError:
        print("❌ MQTT integration not available. Make sure mqtt/ folder exists.")
        return None

def main():
    """Main entry point with comprehensive error handling"""
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()