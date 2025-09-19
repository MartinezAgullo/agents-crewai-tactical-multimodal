import os
from dotenv import load_dotenv
from crewai import Crew, Task
from crewai.utilities import YamlConfigLoader

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key from the environment variable
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class TacticalCrew:
    def __init__(self):
        # Load agents and tasks from the YAML configuration files
        self.config = YamlConfigLoader(config_file='src/tactical/config/agents.yaml').load()
        self.tasks_config = YamlConfigLoader(config_file='src/tactical/config/tasks.yaml').load()['tasks']
        
        self.agents_config = self.config['agents']

    def run(self, mission_report):
        """
        Creates and runs the Crew with the defined agents and tasks.
        """
        # Create Task objects from the loaded configuration
        tasks = []
        for task_name, task_data in self.tasks_config.items():
            tasks.append(
                Task(
                    description=task_data['description'].format(input=mission_report) if 'input' in task_data['description'] else task_data['description'],
                    agent=task_data['agent'],
                    expected_output=task_data['expected_output'],
                    context=[
                        self.tasks_config[ctx_name] for ctx_name in task_data.get('context', [])
                    ],
                )
            )

        # Create the Crew with the loaded agents and tasks
        tactical_crew = Crew(
            agents=self.agents_config,
            tasks=tasks,
            verbose=2, # You can change this to 1 or 0 for less verbosity
        )

        # Kick off the crew's execution with the user's input
        result = tactical_crew.kickoff()
        return result
