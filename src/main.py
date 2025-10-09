import sys
import warnings
import threading
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from tactical.config.config_loader import load_execution_config

# Load environment variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_telemetry(enabled: bool):
    """Configure OpenTelemetry if enabled."""
    if not enabled:
        logger.info("Telemetry disabled")
        return
    
    # Check if OTEL headers are configured
    if not os.getenv('OTEL_EXPORTER_OTLP_HEADERS'):
        logger.warning(
            "Telemetry enabled but OTEL_EXPORTER_OTLP_HEADERS not set in .env\n"
            "Telemetry will not work. See README for OpenObserve setup."
        )
        return
    
    print("Telemetry ENABLED - Initializing instrumentation...")
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
        
        print(f"Telemetry initialized successfully")
        print(f"   Endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')}")
        print(f"   Service: {os.getenv('OTEL_SERVICE_NAME')}")
        
    except ImportError as e:
        logger.error(f"Telemetry dependencies not installed: {e}")
        logger.warning("Install with: uv pip install opentelemetry-api opentelemetry-sdk openinference-instrumentation-crewai openlit")
    except Exception as e:
        logger.error(f"Failed to initialize telemetry: {e}")
        logger.warning("Continuing without telemetry...")


def setup_mqtt_consumer(enabled: bool, crew_instance):
    """Initialize MQTT consumer if enabled."""
    if not enabled:
        logger.info("MQTT consumer disabled")
        return None
    
    try:
        mqtt_path = Path(__file__).parent.parent / 'mqtt'
        if str(mqtt_path) not in sys.path:
            sys.path.insert(0, str(mqtt_path))
        
        from mqtt.mqtt_consumer_agent import MQTTAgentConsumer
        
        logger.info("Initializing MQTT consumer...")
        
        def run_mqtt():
            consumer = MQTTAgentConsumer(
                topics=["Canal 1", "alerts"],
                crew_instance=crew_instance
            )
            consumer.start()
        
        mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
        mqtt_thread.start()
        
        logger.info("MQTT consumer started - listening for tactical alerts")
        return mqtt_thread
        
    except ImportError as e:
        logger.error(f"MQTT consumer module not found: {e}")
        logger.warning("Make sure mqtt/ folder exists and dependencies are installed")
        return None
    except Exception as e:
        logger.error(f"Failed to start MQTT consumer: {e}")
        logger.warning("Continuing without MQTT consumer")
        return None


def run(config):
    """
    Runs the Tactical Crew mission with configured settings.
    This structure is modular and includes robust error handling.
    """
    exec_config = config['execution']
    
    print("\n" + "=" * 60)
    print("INITIALIZING TACTICAL CREW SYSTEM")
    print("=" * 60)
    
    # Import crew
    try:
        from crew import TacticalCrew, test_enhanced_llm_connectivity
    except ImportError as e:
        logger.error(f"Failed to import TacticalCrew: {e}")
        sys.exit(1)
    
    # Test LLM connectivity if manager is enabled
    if exec_config.get('execute_LLM_manager', True):
        print("\nStep 1: Testing LLM connectivity...")
        connectivity_ok = test_enhanced_llm_connectivity()
        
        if not connectivity_ok:
            print("LLM connectivity test failed!")
            sys.exit(1)
        
        print("LLM connectivity test passed!")
    
    # Default mission inputs (can be modified here)
    #mission_input = "inputs/image_inputs/test_image_10_mediterranean_ground.png"
    mission_input = "inputs/audio_inputs/radio_conversation.mp3"
    location_input = None
    
    inputs = {
        'mission_input': mission_input,
        'location_input': location_input
    }
    
    try:
        print("\nStep 2: Initializing Tactical Crew...")
        print("=" * 60)
        
        # Create an instance of the TacticalCrew
        crew_instance = TacticalCrew()
        
        # Initialize MQTT consumer if enabled in config
        mqtt_thread = None
        if exec_config.get('enable_MQTT_consumer', False):
            mqtt_thread = setup_mqtt_consumer(True, crew_instance)
        
        print("\nStep 3: Starting Mission Analysis...")
        print("=" * 60)
        
        # Get the crew object and run the mission
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 60)
        print("TACTICAL ANALYSIS MISSION COMPLETE")
        print("=" * 60)
        print(result)
        
        print("\nMission completed successfully!")
        print("\nReports saved to output/ directory:")
        print("  - threat_analysis_task.md")
        print("  - report_generation_task.md")
        print("  - tactical_response_task.md")
        
        if mqtt_thread:
            print("\nMQTT consumer continues running in background...")
            print("Press Ctrl+C to stop everything")
            
            # Keep main thread alive if MQTT is running
            try:
                mqtt_thread.join()
            except KeyboardInterrupt:
                print("\nStopping MQTT consumer...")
    
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point with comprehensive error handling"""
    
    print("=" * 70)
    print("TACTICAL ANALYSIS SYSTEM - MULTIMODAL CREW")
    print("=" * 70)
    
    # Load execution configuration (centralized)
    config = load_execution_config()
    exec_config = config['execution']
    log_config = config.get('logging', {})
    
    # Apply logging configuration
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    logging.getLogger().setLevel(log_level)
    
    # Suppress OpenLIT logging if present
    logging.getLogger("openlit").setLevel(logging.WARNING)
    
    # Print configuration status
    print("\nCONFIGURATION:")
    print(f"  LLM Manager:     {'ENABLED' if exec_config['execute_LLM_manager'] else 'DISABLED'}")
    print(f"  MQTT Consumer:   {'ENABLED' if exec_config['enable_MQTT_consumer'] else 'DISABLED'}")
    print(f"  Telemetry:       {'ENABLED' if exec_config['enable_telemetry'] else 'DISABLED'}")
    print(f"  Log Level:       {log_config.get('level', 'INFO')}")
    print("=" * 70)
    
    # Setup telemetry based on config
    setup_telemetry(exec_config.get('enable_telemetry', False))
    
    try:
        run(config)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()