import os
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv
from crewai import LLM

logger = logging.getLogger(__name__)

class LLMManager:
    """Enhanced LLM Manager with categorized models and REAL connectivity testing"""
    
    def __init__(self):
        # Model categories
        self.reasoning_models = {}  # A, B, C
        self.flash_models = {}      # A, B, C  
        self.multimodal_models = {} # A, B, C
        self.fallback_model = None
        
        # Track which models are available
        self.available_providers = self._check_available_providers()
        self._setup_categorized_llms()
    
    def _check_available_providers(self) -> Dict[str, bool]:
        """Check which API providers are available"""
        providers = {
            'openai': bool(os.getenv("OPENAI_API_KEY", "").strip()),
            'anthropic': bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
            'google': bool(os.getenv("GOOGLE_API_KEY", "").strip()),
            'deepseek': bool(os.getenv("DEEPSEEK_API_KEY", "").strip()),
            'groq': bool(os.getenv("GROQ_API_KEY", "").strip())
        }
        
        for provider, available in providers.items():
            if available:
                logger.info(f"✅ {provider.title()} API key found")
            else:
                logger.warning(f"❌ {provider.title()} API key not found")
        
        return providers
    
    def _test_llm_with_simple_call(self, llm: LLM, model_name: str) -> bool:
        """Test if an LLM actually works with a simple API call"""
        try:
            # Make a very simple test call
            test_response = llm.call("Hello", callbacks=[])
            if test_response and len(str(test_response).strip()) > 0:
                logger.info(f"✅ {model_name} - Real API test PASSED")
                return True
            else:
                logger.warning(f"❌ {model_name} - Real API test FAILED (empty response)")
                return False
        except Exception as e:
            logger.warning(f"❌ {model_name} - Real API test FAILED: {str(e)[:100]}...")
            return False
    
    def _create_and_test_llm(self, model: str, provider: str = None) -> Optional[LLM]:
        """Create LLM instance with error handling AND real testing"""
        try:
            if provider == 'groq':
                # Groq uses different API base
                llm = LLM(
                    model=model,
                    api_base="https://api.groq.com/openai/v1",
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
            else:
                llm = LLM(
                    model=model,
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
            
            # Now actually TEST the model with a real API call
            if self._test_llm_with_simple_call(llm, model):
                logger.info(f"✅ {model} configured and tested successfully")
                return llm
            else:
                logger.error(f"❌ {model} configured but failed real API test")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to setup {model}: {e}")
            return None
    
    def _setup_categorized_llms(self):
        """Setup LLMs by category with REALISTIC model choices"""
        
        # REASONING MODELS (Use models that actually work)
        reasoning_configs = [
            # A: Use GPT-4 instead of o1-preview (which requires special access)
            ("gpt-4-turbo", "openai") if self.available_providers['openai'] else None,
            # B: Claude 3.5 Sonnet is excellent for reasoning
            ("claude-3-5-sonnet-20241022", "anthropic") if self.available_providers['anthropic'] else None,
            # C: GPT-4 or Gemini Pro as backup
            ("gpt-4", "openai") if self.available_providers['openai'] 
                else ("gemini-1.5-pro", "google") if self.available_providers['google']
                else ("claude-3-sonnet-20240229", "anthropic") if self.available_providers['anthropic'] else None
        ]
        
        for i, config in enumerate(reasoning_configs):
            if config and config[1] and self.available_providers.get(config[1], False):
                model, provider = config
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.reasoning_models[f"reasoning_{chr(65+i)}"] = llm
        
        # FLASH MODELS (Fast and reliable)
        flash_configs = [
            # A: Use Groq if available, otherwise GPT-4o-mini
            ("llama-3.1-70b-versatile", "groq") if self.available_providers['groq']
                else ("gpt-4o-mini", "openai") if self.available_providers['openai'] else None,
            # B: Gemini Flash or Claude Haiku
            ("gemini-1.5-flash", "google") if self.available_providers['google']
                else ("claude-3-haiku-20240307", "anthropic") if self.available_providers['anthropic']
                else ("gpt-3.5-turbo", "openai") if self.available_providers['openai'] else None,
            # C: GPT-3.5 as reliable backup
            ("gpt-3.5-turbo", "openai") if self.available_providers['openai']
                else ("mixtral-8x7b-32768", "groq") if self.available_providers['groq']
                else ("gemini-pro", "google") if self.available_providers['google'] else None
        ]
        
        for i, config in enumerate(flash_configs):
            if config and config[1] and self.available_providers.get(config[1], False):
                model, provider = config
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.flash_models[f"flash_{chr(65+i)}"] = llm
        
        # MULTIMODAL MODELS (Vision-capable models)
        multimodal_configs = [
            # A: GPT-4o (newer and more stable than vision-preview)
            ("gpt-4o", "openai") if self.available_providers['openai'] else None,
            # B: Gemini Pro for multimodal
            ("gemini-1.5-pro", "google") if self.available_providers['google'] else None,
            # C: GPT-4 Turbo as backup
            ("gpt-4-turbo", "openai") if self.available_providers['openai']
                else ("claude-3-5-sonnet-20241022", "anthropic") if self.available_providers['anthropic'] else None
        ]
        
        for i, config in enumerate(multimodal_configs):
            if config and config[1] and self.available_providers.get(config[1], False):
                model, provider = config
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.multimodal_models[f"multimodal_{chr(65+i)}"] = llm
        
        # FALLBACK MODEL (Most reliable - test in order)
        fallback_configs = [
            ("gpt-3.5-turbo", "openai"),
            ("claude-3-haiku-20240307", "anthropic"), 
            ("gemini-pro", "google"),
            ("llama-3.1-8b-instant", "groq"),
        ]
        
        for model, provider in fallback_configs:
            if self.available_providers.get(provider, False):
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.fallback_model = llm
                    break
    
    def get_reasoning_model(self, preference: str = "A") -> Optional[LLM]:
        """Get reasoning model by preference (A, B, or C)"""
        return self.reasoning_models.get(f"reasoning_{preference}")
    
    def get_flash_model(self, preference: str = "A") -> Optional[LLM]:
        """Get flash model by preference (A, B, or C)"""
        return self.flash_models.get(f"flash_{preference}")
    
    def get_multimodal_model(self, preference: str = "A") -> Optional[LLM]:
        """Get multimodal model by preference (A, B, or C)"""
        return self.multimodal_models.get(f"multimodal_{preference}")
    
    def get_fallback_model(self) -> Optional[LLM]:
        """Get the fallback model"""
        return self.fallback_model
    
    def get_best_model_for_task(self, task_type: str) -> LLM:
        """Get the best WORKING model for a specific task type"""
        
        if task_type == "threat_analysis":
            # Use reasoning models for complex threat analysis
            model = (self.get_reasoning_model("A") or 
                    self.get_reasoning_model("B") or 
                    self.get_reasoning_model("C") or 
                    self.get_fallback_model())
        
        elif task_type == "report_generation":
            # Use flash models for quick report generation
            model = (self.get_flash_model("A") or 
                    self.get_flash_model("B") or 
                    self.get_flash_model("C") or 
                    self.get_fallback_model())
        
        elif task_type == "tactical_advisor":
            # Use reasoning models for strategic thinking
            model = (self.get_reasoning_model("A") or 
                    self.get_multimodal_model("A") or
                    self.get_reasoning_model("B") or 
                    self.get_fallback_model())
        
        elif task_type == "multimodal":
            # Use multimodal models for image/document analysis
            model = (self.get_multimodal_model("A") or 
                    self.get_multimodal_model("B") or 
                    self.get_multimodal_model("C") or 
                    self.get_fallback_model())
        
        else:
            # Default: try reasoning first, then flash, then fallback
            model = (self.get_reasoning_model("A") or 
                    self.get_flash_model("A") or 
                    self.get_fallback_model())
        
        if not model:
            raise RuntimeError("No working LLM models available for any task!")
        
        logger.info(f"🎯 Selected {model.model} for {task_type}")
        return model
    
    def get_available_models_count(self) -> Dict[str, int]:
        """Get count of available models by category"""
        return {
            'reasoning': len(self.reasoning_models),
            'flash': len(self.flash_models), 
            'multimodal': len(self.multimodal_models),
            'fallback': 1 if self.fallback_model else 0
        }
    
    def print_enhanced_status(self):
        """Print detailed status of all model categories with complete A/B/C listing"""
        print("\n" + "="*70)
        print("🤖 LLM CONFIGURATION STATUS (TESTED MODELS)")
        print("="*70)

        # Multimodal Models - threat_analyst_agent
        print("\n🎨 Multimodal models :: For input processing")
        for letter in ['A', 'B', 'C']:
            key = f"multimodal_{letter}"
            model_name = f"Multimodal Model {letter}"
            llm = self.multimodal_models.get(key)
            if llm:
                status = f"✅ {llm.model}"
            else:
                status = "❌ not configured"
            print(f"  {model_name:<20} {status}")

        # Flash Models - For report_generator_agent
        print("\n⚡ Flash models :: Message editing")
        for letter in ['A', 'B', 'C']:
            key = f"flash_{letter}"
            model_name = f"Flash Model {letter}"
            llm = self.flash_models.get(key)
            if llm:
                status = f"✅ {llm.model}"
            else:
                status = "❌ not configured"
            print(f"  {model_name:<20} {status}")

        # Reasoning Models - tactical_advisor_agent
        print("\n🧠 Reasoning models :: Tactical organisation")
        for letter in ['A', 'B', 'C']:
            key = f"reasoning_{letter}"
            model_name = f"Reasoning Model {letter}"
            llm = self.reasoning_models.get(key)
            if llm:
                status = f"✅ {llm.model}"
            else:
                status = "❌ not configured"
            print(f"  {model_name:<20} {status}")
        
        # Fallback Model
        print("\n🛡️  Fallback model :: Emergency backup")
        fallback_status = f"✅ {self.fallback_model.model}" if self.fallback_model else "❌ not configured"
        print(f"  Fallback Model      {fallback_status}")
        
        # Summary
        counts = self.get_available_models_count()
        total_models = sum(counts.values())
        
        print(f"\n📊 SUMMARY")
        print(f"  Total WORKING Models: {total_models}")
        print(f"  Reasoning: {counts['reasoning']}/3")
        print(f"  Flash: {counts['flash']}/3")
        print(f"  Multimodal: {counts['multimodal']}/3") 
        print(f"  Fallback: {counts['fallback']}/1")

        if total_models == 0:
            print("\n❌ WARNING: No working models found!")
            print("   This usually means:")
            print("   - API keys are invalid/expired")
            print("   - No internet connection") 
            print("   - Models require special access (like o1-preview)")
        else:
            print(f"\n✅ SUCCESS: {total_models} models are working and ready!")
        
        print("="*70 + "\n")