import os
import yaml
import logging
from typing import Optional
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI API key from the environment variable
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FallbackLLMManager:
    """Manages LLM fallback logic with connectivity testing"""
    
    def __init__(self):
        self.primary_llm = None
        self.fallback_llm = None
        self.tertiary_llm = None
        self.quaternary_llm = None
        self._setup_llms()
    
    def _test_api_key(self, api_key: str, provider_name: str) -> bool:
        """Test if API key exists and is not empty"""
        if not api_key or api_key.strip() == "":
            logger.warning(f"❌ {provider_name} API key not found or empty")
            return False
        logger.info(f"✅ {provider_name} API key found")
        return True
    
    def _setup_llms(self):
        """Setup LLMs in order of preference with fallback chain"""
        
        # Primary LLM (OpenAI GPT-4 Turbo)
        if self._test_api_key(os.getenv("OPENAI_API_KEY", ""), "OpenAI"):
            try:
                self.primary_llm = LLM(
                    model="gpt-4-turbo",
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
                logger.info("🚀 Primary LLM: OpenAI GPT-4 Turbo configured")
            except Exception as e:
                logger.error(f"Failed to setup OpenAI GPT-4 Turbo: {e}")
        
        # Fallback LLM (Anthropic Claude)
        if self._test_api_key(os.getenv("ANTHROPIC_API_KEY", ""), "Anthropic"):
            try:
                self.fallback_llm = LLM(
                    model="claude-3-sonnet-20240229",
                    drop_params=True
                )
                logger.info("🔄 Fallback LLM: Anthropic Claude 3 Sonnet configured")
            except Exception as e:
                logger.error(f"Failed to setup Anthropic Claude: {e}")
        
        # Tertiary LLM (Google Gemini)
        if self._test_api_key(os.getenv("GOOGLE_API_KEY", ""), "Google"):
            try:
                self.tertiary_llm = LLM(
                    model="gemini-pro",
                    drop_params=True
                )
                logger.info("🔄 Tertiary LLM: Google Gemini Pro configured")
            except Exception as e:
                logger.error(f"Failed to setup Google Gemini: {e}")
        
        # Quaternary LLM (OpenAI GPT-3.5 as final fallback)
        if self._test_api_key(os.getenv("OPENAI_API_KEY", ""), "OpenAI (GPT-3.5)"):
            try:
                self.quaternary_llm = LLM(
                    model="gpt-3.5-turbo",
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
                logger.info("🔄 Quaternary LLM: OpenAI GPT-3.5 Turbo configured")
            except Exception as e:
                logger.error(f"Failed to setup OpenAI GPT-3.5: {e}")
    
    def get_primary_llm(self) -> Optional[LLM]:
        """Get the primary LLM if available"""
        return self.primary_llm
    
    def get_fallback_llm(self) -> Optional[LLM]:
        """Get the best available fallback LLM"""
        return self.fallback_llm or self.tertiary_llm or self.quaternary_llm
    
    def get_best_available_llm(self) -> LLM:
        """Get the best available LLM with fallback chain"""
        if self.primary_llm:
            logger.info("🎯 Using Primary LLM: GPT-4 Turbo")
            return self.primary_llm
        elif self.fallback_llm:
            logger.warning("🔄 Using Fallback LLM: Claude 3 Sonnet")
            return self.fallback_llm
        elif self.tertiary_llm:
            logger.warning("🔄 Using Tertiary LLM: Gemini Pro")
            return self.tertiary_llm
        elif self.quaternary_llm:
            logger.warning("🔄 Using Final Fallback LLM: GPT-3.5 Turbo")
            return self.quaternary_llm
        else:
            raise RuntimeError("""
❌ No LLM providers are available. Please configure at least one API key:
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - GOOGLE_API_KEY

Example:
export OPENAI_API_KEY='your-openai-key-here'
            """)
    
    def get_llm_for_agent(self, agent_type: str = "default") -> LLM:
        """Get appropriate LLM for specific agent types"""
        # You can customize LLM selection based on agent type
        if agent_type == "threat_analyst":
            # Prefer more analytical models for threat analysis
            return self.primary_llm or self.fallback_llm or self.get_best_available_llm()
        elif agent_type == "report_generator":
            # Any good model works for report generation
            return self.get_best_available_llm()
        elif agent_type == "tactical_advisor":
            # Prefer strategic thinking models
            return self.primary_llm or self.fallback_llm or self.get_best_available_llm()
        else:
            return self.get_best_available_llm()

    def print_llm_status(self):
        """Print current LLM configuration status"""
        print("\n" + "="*60)
        print("🤖 LLM CONFIGURATION STATUS")
        print("="*60)
        
        llms = [
            ("Primary (GPT-4 Turbo)", self.primary_llm),
            ("Fallback (Claude 3 Sonnet)", self.fallback_llm),
            ("Tertiary (Gemini Pro)", self.tertiary_llm),
            ("Final Fallback (GPT-3.5)", self.quaternary_llm)
        ]
        
        for name, llm in llms:
            status = "✅ Available" if llm else "❌ Not configured"
            print(f"{name:<30} {status}")
        
        active_llm = self.get_best_available_llm()
        print(f"\n🎯 Active LLM: {active_llm.model}")
        print("="*60 + "\n")


@CrewBase
class TacticalCrew:
    """Tactical Response Crew"""
    
    # Use file paths for the @CrewBase decorator to automatically handle loading
    agents_config = 'tactical/config/agents.yaml'
    tasks_config = 'tactical/config/tasks.yaml'

    def __init__(self):
        super().__init__()
        # Initialize LLM manager
        self.llm_manager = FallbackLLMManager()
        self.llm_manager.print_llm_status()
    
    @agent
    def threat_analyst_agent(self) -> Agent:
        """
        Agent to analyze and identify hostile presences from a field report.
        """
        agent_config = dict(self.agents_config['threat_analyst_agent'])
        
        # Override LLM with fallback-enabled LLM
        agent_config['llm'] = self.llm_manager.get_llm_for_agent('threat_analyst')
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def report_generator_agent(self) -> Agent:
        """
        Agent to create a professional situation report.
        """
        agent_config = dict(self.agents_config['report_generator_agent'])
        
        # Override LLM with fallback-enabled LLM
        agent_config['llm'] = self.llm_manager.get_llm_for_agent('report_generator')
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False
        )
    
    @agent
    def tactical_advisor_agent(self) -> Agent:
        """
        Agent to suggest a tactical response based on the situation.
        """
        agent_config = dict(self.agents_config['tactical_advisor_agent'])
        
        # Override LLM with fallback-enabled LLM
        agent_config['llm'] = self.llm_manager.get_llm_for_agent('tactical_advisor')
        
        return Agent(
            config=agent_config,
            verbose=True,
            allow_delegation=False
        )

    @task
    def threat_analysis_task(self, **kwargs) -> Task:
        """
        Task for the Threat Analyst agent to analyze the mission report.
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
        Creates the Tactical Crew with the defined agents and tasks.
        """
        try:
            crew_llm = self.llm_manager.get_best_available_llm()

            crew = Crew(
                agents=self.agents,  # Automatically created by the @agent decorator
                tasks=self.tasks,   # Automatically created by the @task decorator
                process=Process.sequential,
                verbose=True,
                full_output=True, # Enable saving full outputs
                output_folder='output', # Specify the output folder
                llm=crew_llm
            )
            
            # Add fallback LLM if available and supported by CrewAI version
            fallback_llm = self.llm_manager.get_fallback_llm()
            if fallback_llm and hasattr(crew, 'fallback_llm'):
                crew.fallback_llm = fallback_llm
                logger.info(f"🔄 Crew fallback LLM set to: {fallback_llm.model}")
            
            return crew
            
        except Exception as e:
            logger.error(f"❌ Failed to create crew: {e}")
            raise RuntimeError(f"Cannot create crew: {e}")


def test_llm_connectivity():
    """Test function to verify LLM connectivity"""
    logger.info("🧪 Testing LLM connectivity...")
    try:
        manager = FallbackLLMManager()
        llm = manager.get_best_available_llm()
        logger.info(f"✅ Successfully configured LLM: {llm.model}")
        return True, manager
    except Exception as e:
        logger.error(f"❌ LLM connectivity test failed: {e}")
        return False, None