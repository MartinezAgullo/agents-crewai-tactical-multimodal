import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key from the environment variable
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

@CrewBase
class TacticalCrew:
    """Tactical Response Crew"""
    
    # Use file paths for the @CrewBase decorator to automatically handle loading
    agents_config = 'tactical/config/agents.yaml'
    tasks_config = 'tactical/config/tasks.yaml'
    
    @agent
    def threat_analyst(self) -> Agent:
        """
        Agent to analyze and identify hostile presences from a field report.
        """
        return Agent(
            config=self.agents_config['threat_analyst'],
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        """
        Agent to create a professional situation report.
        """
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True
        )
    
    @agent
    def tactical_advisor(self) -> Agent:
        """
        Agent to suggest a tactical response based on the situation.
        """
        return Agent(
            config=self.agents_config['tactical_advisor'],
            verbose=True
        )

    @task
    def threat_analysis(self, **kwargs: str) -> Task:
        """
        Task for the Threat Analyst agent to analyze the mission report.
        """
        return Task(
            config=self.tasks_config['threat_analysis'],
            agent=self.threat_analyst(),
            inputs=kwargs
        )

    @task
    def report_generation(self) -> Task:
        """
        Task for the Report Generator agent to create a situation report.
        """
        return Task(
            config=self.tasks_config['report_generation'],
            agent=self.report_generator(),
            context=[self.threat_analysis()]
            
        )

    @task
    def tactical_response(self) -> Task:
        """
        Task for the Tactical Advisor agent to suggest a response.
        """
        return Task(
            config=self.tasks_config['tactical_response'],
            agent=self.tactical_advisor(),
            context=[self.report_generation()]
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
