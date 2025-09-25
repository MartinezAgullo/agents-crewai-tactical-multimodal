import os
import yaml
import logging
from typing import Optional
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Import custom multimodal tools
from src.tactical.tools.multimodal_tools import (
    AudioTranscriptionTool,
    DocumentAnalysisTool,
    InputTypeDeterminerTool
)

# Import the tools for location context
from src.tactical.tools.location_tools import LocationContextTool


# Import the enhanced LLM manager
from llm_manager import LLMManager

# Load environment variables from .env file
load_dotenv()

# Set up API keys from environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_API_KEY", "")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY", "")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@CrewBase
class TacticalCrew:
    """Tactical Response Crew with LLM support and multimodal processing"""
    
    # Use file paths for the @CrewBase decorator to automatically handle loading
    agents_config = 'tactical/config/agents.yaml'
    tasks_config = 'tactical/config/tasks.yaml'

    def __init__(self):
        super().__init__()
        # Initialize Enhanced LLM manager
        self.llm_manager = LLMManager()
        self.llm_manager.print_enhanced_status()

        # Initialize multimodal processing and custom tools
        self.custom_tools = self._setup_custom_tools()
    
    def _setup_custom_tools(self):
        """Initialize the multimodal processing and location tools"""
        return [
            InputTypeDeterminerTool(),
            AudioTranscriptionTool(),
            DocumentAnalysisTool(),
            LocationContextTool()
        ]
    
    @agent
    def threat_analyst_agent(self) -> Agent:
        """
        Agent to analyze and identify hostile presences from a field report.
        Uses reasoning models for complex threat analysis.
        Can process text, audio, images, and documents.
        """
        agent_config = dict(self.agents_config['threat_analyst_agent'])
        
        # Use multimodal-capable reasoning model
        agent_config['llm'] = self.llm_manager.get_best_model_for_task('threat_analysis')

        # Add multimodal processing and location tools
        if 'tools' not in agent_config:
            agent_config['tools'] = []
        agent_config['tools'].extend(self.custom_tools)
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False,
            multimodal=True # AddImageTool is automatically included
        )

    @agent
    def report_generator_agent(self) -> Agent:
        """
        Agent to create a professional situation report.
        Uses flash models for quick report generation.
        """
        agent_config = dict(self.agents_config['report_generator_agent'])
        
        # Use flash model for quick report generation
        agent_config['llm'] = self.llm_manager.get_best_model_for_task('report_generation')
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def tactical_advisor_agent(self) -> Agent:
        """
        Agent to suggest a tactical response based on the situation.
        Uses reasoning models for strategic thinking.
        """
        agent_config = dict(self.agents_config['tactical_advisor_agent'])
        
        # Use reasoning model for strategic tactical advice
        agent_config['llm'] = self.llm_manager.get_best_model_for_task('tactical_advisor')
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False
        )

    @task
    def threat_analysis_task(self, **kwargs) -> Task:
        """
        Task for the Threat Analyst agent to analyze the mission report.
        The agent will automatically determine input type and process accordingly.
        """
        
        return Task(
            config=self.tasks_config['threat_analysis_task'],
            agent=self.threat_analyst_agent(),
            inputs=kwargs
        )

    @task
    def report_generation_task(self) -> Task:
        """
        Task for the Report Generator agent to create a situation report.
        """
        return Task(
            config=self.tasks_config['report_generation_task'],
            agent=self.report_generator_agent(),
            context=[self.threat_analysis_task()]
        )

    @task
    def tactical_response_task(self) -> Task:
        """
        Task for the Tactical Advisor agent to suggest a response.
        """
        return Task(
            config=self.tasks_config['tactical_response_task'],
            agent=self.tactical_advisor_agent(),
            context=[self.report_generation_task()]
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the Tactical Crew with muultimodal processing.
        """
        try:
            # Use the best reasoning model for crew-wide operations
            crew_llm = self.llm_manager.get_best_model_for_task('default')
            
            if not crew_llm:
                raise RuntimeError("No LLM models available for crew operations")

            crew = Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.sequential,
                verbose=True,
                full_output=True,
                output_folder='output',
                llm=crew_llm
            )
            
            logger.info(f"Tactical Crew configured")
            logger.info(f" Primary LLM: {crew_llm.model}")
            logger.info(f" Available tools: {len(self.custom_tools)} multimodal processing and gelolocation tools")
            
            return crew
            
        except Exception as e:
            logger.error(f"❌ Failed to create crew: {e}")
            raise RuntimeError(f"Cannot create crew: {e}")


def test_enhanced_llm_connectivity():
    """Enhanced test function to verify all LLM categories"""
    logger.info("🧪 Testing Enhanced LLM connectivity...")
    
    try:
        manager = LLMManager()
        
        # Test each category
        tests = [
            ("Reasoning", manager.get_reasoning_model("A")),
            ("Flash", manager.get_flash_model("A")),
            ("Multimodal", manager.get_multimodal_model("A")),
            ("Fallback", manager.get_fallback_model())
        ]
        
        working_models = 0
        for category, model in tests:
            if model:
                logger.info(f"✅ {category} model available: {model.model}")
                working_models += 1
            else:
                logger.warning(f"❌ No {category} model available")
        
        if working_models > 0:
            logger.info(f"✅ Enhanced LLM test passed! {working_models}/4 categories available")
            return True
        else:
            logger.error("❌ No LLM models available in any category")
            return False
            
    except Exception as e:
        logger.error(f"❌ Enhanced LLM connectivity test failed: {e}")
        return False
