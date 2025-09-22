import sys
import warnings
from crew import TacticalCrew, test_enhanced_llm_connectivity

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
    
    # A hardcoded mission report for demonstration purposes
    mission_report = """
    Field Report:

    Observer: Recon Team 7
    Date/Time: 14:30 Zulu, 19 SEP 2025
    Location: Coordinates 40.4168° N, 3.7038° W.

    Details:
    We have observed a group of approximately 15 infantry soldiers in a wooded area near the
    abandoned factory. They appear to be establishing a defensive position.
    Approximately 500 meters to the east, we identified three T-90 battle tanks
    moving slowly along a dirt road, heading towards the factory. They are supported
    by what appears to be a mobile anti-air missile system. No other activity observed.
    """

    inputs = {
        'mission_report': f"{mission_report}"
    }
    
    try:
        print("\n🚀 Step 2: Initializing Tactical Crew...")
        print("="*60)
        
        # Create an instance of the TacticalCrew
        crew_instance = TacticalCrew()
        
        print("\n🎯 Step 3: Starting Mission Analysis...")
        print("="*60)
        
        # Get the crew object and run the mission
        result = crew_instance.crew().kickoff(inputs=inputs)

        print("\n" + "="*60)
        print("🎖️  TACTICAL ANALYSIS MISSION COMPLETE")
        print("="*60)
        print(result)
        
        print("\n✅ Mission completed successfully!")

    except Exception as e:
        print(f"\n❌ An error occurred while running the crew: {e}", file=sys.stderr)
        sys.exit(1)

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