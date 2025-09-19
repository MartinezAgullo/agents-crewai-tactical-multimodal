import sys
import warnings
from crew import TacticalCrew

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Runs the Tactical Crew mission with a hardcoded mission report.
    This structure is modular and includes robust error handling.
    """
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
        print("### Starting the Tactical Crew Mission ###")
        
        # Create an instance of the TacticalCrew
        crew_instance = TacticalCrew()
        
        # Get the crew object and run the mission
        result = crew_instance.crew().kickoff(inputs=inputs)

        print("\n### Final Tactical Response ###")
        print(result)

    except Exception as e:
        print(f"An error occurred while running the crew: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run()
