import os
import logging
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from crewai import LLM

logger = logging.getLogger(__name__)

class LLMManager:
    """Enhanced LLM Manager with expanded model categories and real connectivity testing"""
    
    def __init__(self):
        # Model categories - now supporting more than 3 models per category
        self.reasoning_models = {}  # A, B, C, D, E, F...
        self.flash_models = {}      # A, B, C, D, E...
        self.multimodal_models = {} # A, B, C, D, E...
        self.fallback_model = None
        
        # Track attempted configurations for better error reporting
        self.attempted_configs = {
            'reasoning': {},
            'flash': {},
            'multimodal': {},
            'fallback': []
        }
        
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
            'groq': bool(os.getenv("GROQ_API_KEY", "").strip()),
            'mistral': bool(os.getenv("MISTRAL_API_KEY", "").strip())
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
            elif provider == 'google':
                # For Google Gemini models
                llm = LLM(
                    model=model,
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
            elif provider == 'mistral':
                # For Mistral models
                llm = LLM(
                    model=model,
                    drop_params=True,
                    additional_drop_params=["stop"]
                )
            elif provider == 'deepseek':
                # For DeepSeek models
                llm = LLM(
                    model=model,
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
        """Setup LLMs by category with expanded model support"""
        
        # REASONING MODELS - Expanded list for complex analysis
        reasoning_configs = [
            # Tier 1: Premium reasoning models
            ("gpt-4-turbo", "openai"),
            ("claude-3-5-sonnet-20241022", "anthropic"),
            ("gemini-2.0-flash-exp", "google"),  # Gemini 2.0 Flash Experimental for reasoning
            
            # Tier 2: Strong reasoning alternatives
            ("gpt-4", "openai"),
            ("mistral-large-2411", "mistral"),  # Mistral Large
            ("deepseek-r1-distill-llama-70b", "deepseek"),  # DeepSeek R1 Distill
            
            # Tier 3: Additional reasoning options
            ("qwen/qwen-2.5-72b-instruct", "groq"),  # Qwen 3 32B via Groq (actual model name)
            ("llama-3.3-70b-versatile", "groq"),  # Llama as reasoning fallback
        ]
        
        for i, (model, provider) in enumerate(reasoning_configs):
            letter = chr(65+i)  # A, B, C, D, E, F, G, H
            if self.available_providers.get(provider, False):
                self.attempted_configs['reasoning'][letter] = model
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.reasoning_models[f"reasoning_{letter}"] = llm
            else:
                self.attempted_configs['reasoning'][letter] = f"{model} (no {provider} key)"
        
        # FLASH MODELS - Expanded for fast responses
        flash_configs = [
            # Tier 1: Fastest models
            ("llama-3.3-70b-versatile", "groq"),
            ("llama-3.1-8b-instant", "groq"),
            ("gemini-2.0-flash-exp", "google"),  # Gemini 2.0 Flash
            
            # Tier 2: Fast alternatives
            ("gpt-4o-mini", "openai"),
            ("gpt-3.5-turbo", "openai"),
            ("claude-3-haiku-20240307", "anthropic"),
            
            # Tier 3: Additional fast options
            ("mistral-small-2409", "mistral"),  # Mistral Small for fast responses
        ]
        
        for i, (model, provider) in enumerate(flash_configs):
            letter = chr(65+i)  # A, B, C, D, E, F, G
            if self.available_providers.get(provider, False):
                self.attempted_configs['flash'][letter] = model
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.flash_models[f"flash_{letter}"] = llm
            else:
                self.attempted_configs['flash'][letter] = f"{model} (no {provider} key)"
        
        # MULTIMODAL MODELS - Expanded for vision and complex input
        multimodal_configs = [
            # Tier 1: Best multimodal
            ("gpt-4o", "openai"),
            ("gemini-2.0-flash-exp", "google"),  # Gemini 2.0 for multimodal
            ("gpt-4-turbo", "openai"),
            
            # Tier 2: Alternative multimodal
            ("gpt-4", "openai"),
            ("claude-3-5-sonnet-20241022", "anthropic"),  # Claude for text analysis
            
            # Tier 3: Fallback multimodal
            ("gpt-4o-mini", "openai"),
        ]
        
        for i, (model, provider) in enumerate(multimodal_configs):
            letter = chr(65+i)  # A, B, C, D, E, F
            if self.available_providers.get(provider, False):
                self.attempted_configs['multimodal'][letter] = model
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.multimodal_models[f"multimodal_{letter}"] = llm
            else:
                self.attempted_configs['multimodal'][letter] = f"{model} (no {provider} key)"
        
        # FALLBACK MODEL - Most reliable options
        fallback_configs = [
            ("gpt-3.5-turbo", "openai"),
            ("claude-3-haiku-20240307", "anthropic"), 
            ("llama-3.1-8b-instant", "groq"),
            ("mistral-small-2409", "mistral"),
        ]
        
        for model, provider in fallback_configs:
            self.attempted_configs['fallback'].append(model)
            if self.available_providers.get(provider, False):
                llm = self._create_and_test_llm(model, provider)
                if llm:
                    self.fallback_model = llm
                    break
    
    def get_reasoning_model(self, preference: str = "A") -> Optional[LLM]:
        """Get reasoning model by preference (A, B, C, D, E, F, G, H)"""
        return self.reasoning_models.get(f"reasoning_{preference}")
    
    def get_flash_model(self, preference: str = "A") -> Optional[LLM]:
        """Get flash model by preference (A, B, C, D, E, F, G)"""
        return self.flash_models.get(f"flash_{preference}")
    
    def get_multimodal_model(self, preference: str = "A") -> Optional[LLM]:
        """Get multimodal model by preference (A, B, C, D, E, F)"""
        return self.multimodal_models.get(f"multimodal_{preference}")
    
    def get_fallback_model(self) -> Optional[LLM]:
        """Get the fallback model"""
        return self.fallback_model
    
    def get_best_model_for_task(self, task_type: str) -> LLM:
        """Get the best WORKING model for a specific task type"""
        
        if task_type == "threat_analysis":
            # Try reasoning models in order
            for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                model = self.get_reasoning_model(letter)
                if model:
                    return model
            return self.get_fallback_model()
        
        elif task_type == "report_generation":
            # Try flash models in order
            for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                model = self.get_flash_model(letter)
                if model:
                    return model
            return self.get_fallback_model()
        
        elif task_type == "tactical_advisor":
            # Try reasoning first, then multimodal
            for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                model = self.get_reasoning_model(letter)
                if model:
                    return model
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                model = self.get_multimodal_model(letter)
                if model:
                    return model
            return self.get_fallback_model()
        
        elif task_type == "multimodal":
            # Try multimodal models in order
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                model = self.get_multimodal_model(letter)
                if model:
                    return model
            return self.get_fallback_model()
        
        else:
            # Default: try reasoning first, then flash, then fallback
            for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                model = self.get_reasoning_model(letter)
                if model:
                    return model
            for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                model = self.get_flash_model(letter)
                if model:
                    return model
            return self.get_fallback_model()
        
        if not self.get_fallback_model():
            raise RuntimeError("No working LLM models available for any task!")
        
        logger.info(f"🎯 Selected {self.get_fallback_model().model} for {task_type}")
        return self.get_fallback_model()
    
    def get_available_models_count(self) -> Dict[str, int]:
        """Get count of available models by category"""
        return {
            'reasoning': len(self.reasoning_models),
            'flash': len(self.flash_models), 
            'multimodal': len(self.multimodal_models),
            'fallback': 1 if self.fallback_model else 0
        }
    
    def print_enhanced_status(self):
        """Print detailed status of all model categories with expanded listing"""
        print("\n" + "="*70)
        print("🤖 LLM CONFIGURATION STATUS (EXPANDED MODELS)")
        print("="*70)

        # Reasoning Models - expanded list
        print("\n Reasoning models :: Tactical analysis & strategy")
        reasoning_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for letter in reasoning_letters:
            key = f"reasoning_{letter}"
            model_name = f"Reasoning Model {letter}"
            llm = self.reasoning_models.get(key)
            attempted_model = self.attempted_configs['reasoning'].get(letter, "")
            
            if llm:
                status = f"✅ {llm.model}"
            elif attempted_model:
                status = f"❌ {attempted_model} not configured"
            else:
                continue  # Skip if no attempt was made
            print(f"  {model_name:<20} {status}")

        # Flash Models - expanded list  
        print("\n Flash models :: Fast responses & editing")
        flash_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        for letter in flash_letters:
            key = f"flash_{letter}"
            model_name = f"Flash Model {letter}"
            llm = self.flash_models.get(key)
            attempted_model = self.attempted_configs['flash'].get(letter, "")
            
            if llm:
                status = f"✅ {llm.model}"
            elif attempted_model:
                status = f"❌ {attempted_model} not configured"
            else:
                continue
            print(f"  {model_name:<20} {status}")

        # Multimodal Models - expanded list
        print("\n Multimodal models :: Vision & complex input")
        multimodal_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        for letter in multimodal_letters:
            key = f"multimodal_{letter}"
            model_name = f"Multimodal Model {letter}"
            llm = self.multimodal_models.get(key)
            attempted_model = self.attempted_configs['multimodal'].get(letter, "")
            
            if llm:
                status = f"✅ {llm.model}"
            elif attempted_model:
                status = f"❌ {attempted_model} not configured"
            else:
                continue
            print(f"  {model_name:<20} {status}")
        
        # Fallback Model
        print("\n  Fallback model :: Emergency backup")
        if self.fallback_model:
            fallback_status = f"✅ {self.fallback_model.model}"
        else:
            attempted_models = ", ".join(self.attempted_configs['fallback'][:3])  # Show first 3
            fallback_status = f"❌ {attempted_models}... not configured"
        print(f"  Fallback Model      {fallback_status}")
        
        # Summary
        counts = self.get_available_models_count()
        total_models = sum(counts.values())
        
        print(f"\n📊 SUMMARY")
        print(f"  Total WORKING Models: {total_models}")
        print(f"  Reasoning: {counts['reasoning']}/{len(reasoning_letters)}")
        print(f"  Flash: {counts['flash']}/{len(flash_letters)}")
        print(f"  Multimodal: {counts['multimodal']}/{len(multimodal_letters)}") 
        print(f"  Fallback: {counts['fallback']}/1")

        if total_models == 0:
            print("\n❌ WARNING: No working models found!")
            print("   Check your API keys and network connection")
        elif total_models < 5:
            print(f"\n⚠️  LIMITED: Only {total_models} models working")
            print("   To unlock more models, add these API keys:")
            if not self.available_providers.get('google'):
                print("   • GOOGLE_API_KEY for Gemini 2.0 models")
            if not self.available_providers.get('mistral'):
                print("   • MISTRAL_API_KEY for Mistral Large")
            if not self.available_providers.get('deepseek'):
                print("   • DEEPSEEK_API_KEY for DeepSeek R1 Distill")
        else:
            print(f"\n✅ SUCCESS: {total_models} models are working and ready!")
            print("   You have excellent model diversity!")
        
        print("="*70 + "\n")