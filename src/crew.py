import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key from the environment variable
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

@CrewBase
class TacticalCrew:
    """Tactical Response Crew"""
    
    # Path to the agents and tasks configuration files
    gents_config = 'tactical/config/agents.yaml'
    tasks_config = 'tactical/config/tasks.yaml'

    def __init__(self):
        # The __init__ method is where you would handle any custom initialization.
        # CrewAI's decorators handle most of the configuration automatically.
        pass

    @agent
    def threat_analyst(self) -> Agent:
        """
        Agent to analyze and identify hostile presences from a field report.
        """
        return Agent(
            config=self.agents_config['Threat Analyst'],
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        """
        Agent to create a professional situation report.
        """
        return Agent(
            config=self.agents_config['Report Generator'],
            verbose=True
        )
    
    @agent
    def tactical_advisor(self) -> Agent:
        """
        Agent to suggest a tactical response based on the situation.
        """
        return Agent(
            config=self.agents_config['Tactical Advisor'],
            verbose=True
        )

    @task
    def threat_analysis(self, mission_report: str) -> Task:
        """
        Task for the Threat Analyst agent to analyze the mission report.
        """
        return Task(
            config=self.tasks_config['threat_analysis'],
            agent=self.threat_analyst(),
            output_file=self.tasks_config['threat_analysis']['output_file'],
            context=[],
            inputs={'input': mission_report}
        )

    @task
    def report_generation(self) -> Task:
        """
        Task for the Report Generator agent to create a situation report.
        """
        return Task(
            config=self.tasks_config['report_generation'],
            agent=self.report_generator(),
            output_file=self.tasks_config['report_generation']['output_file'],
            context=[self.threat_analysis]
        )

    @task
    def tactical_response(self) -> Task:
        """
        Task for the Tactical Advisor agent to suggest a response.
        """
        return Task(
            config=self.tasks_config['tactical_response'],
            agent=self.tactical_advisor(),
            output_file=self.tasks_config['tactical_response']['output_file'],
            context=[self.report_generation]
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the Tactical Crew with the defined agents and tasks.
        """
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,   # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            full_output=True, # Enable saving full outputs
            output_folder='output' # Specify the output folder
        )
