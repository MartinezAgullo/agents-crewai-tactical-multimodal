from crewai.tools import BaseTool
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ClassificationInput(BaseModel):
    """Input schema for entity classification."""
    entity_description: str = Field(
        ..., 
        description="Detailed description of the observed entity (uniform, insignia, weapons, behavior)"
    )
    context: Optional[str] = Field(
        None,
        description="Additional tactical context (location, activity, associated entities)"
    )


class ClassificationReferenceTool(BaseTool):
    name: str = "Classification Reference Tool"
    description: str = (
        "Authoritative tool for classifying detected entities as Friend, Foe, Civilian, or Unknown. "
        "Provides official classification rules based on uniform patterns, insignia, equipment, and behavior. "
        "Use this tool for EVERY entity detected to ensure consistent, accurate classification."
    )
    args_schema: Type[BaseModel] = ClassificationInput
    
    # Store as regular dict, not a Pydantic field
    _classification_rules: Optional[Dict[str, Any]] = None
    
    @model_validator(mode='after')
    def load_rules(self):
        """Load classification rules after model initialization."""
        if self._classification_rules is None:
            self._load_classifications()
        return self
    
    def _load_classifications(self):
        """Load classification rules from YAML with error handling."""
        try:
            config_path = Path(__file__).parent.parent / "config" / "classifications.yaml"
            
            if not config_path.exists():
                raise FileNotFoundError(
                    f"Classification rules file not found at: {config_path}\n"
                    f"Please ensure classifications.yaml exists in: src/tactical/config/"
                )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_rules = yaml.safe_load(f)
            
            # Validate that the YAML has the expected structure
            if not loaded_rules or 'classification_rules' not in loaded_rules:
                raise ValueError(
                    f"Invalid classification rules format in {config_path}\n"
                    f"Expected 'classification_rules' key at root level"
                )
            
            # Store directly as class attribute (not through Pydantic)
            object.__setattr__(self, '_classification_rules', loaded_rules)
            
            logger.info(f"✅ Classification rules loaded successfully from {config_path}")
            
        except FileNotFoundError as e:
            logger.error(f"❌ Classification file not found: {e}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"❌ Error parsing classifications.yaml: {e}")
            raise ValueError(f"Invalid YAML format in classifications.yaml: {e}")
        except Exception as e:
            logger.error(f"❌ Unexpected error loading classification rules: {e}")
            raise
    
    def _run(self, entity_description: str, context: Optional[str] = None) -> str:
        """
        Return classification guidance based on entity description.
        
        Args:
            entity_description: Observable characteristics of the entity
            context: Additional tactical context
            
        Returns:
            Formatted classification guidance with relevant rules
        """
        # Lazy load if needed
        if self._classification_rules is None:
            self._load_classifications()
        
        if not self._classification_rules:
            return "ERROR: Classification rules not loaded. Please check classifications.yaml file."
        
        rules = self._classification_rules['classification_rules']
        
        # Build comprehensive reference
        output = [
            "=" * 70,
            "ENTITY CLASSIFICATION REFERENCE",
            "=" * 70,
            f"\nENTITY DESCRIPTION: {entity_description}",
        ]
        
        if context:
            output.append(f"CONTEXT: {context}\n")
        
        output.extend([
            "\n" + "=" * 70,
            "CLASSIFICATION CRITERIA:",
            "=" * 70,
        ])
        
        # Friends
        output.append("\n[FRIENDS - Allied Forces]")
        output.append(f"Description: {rules['friends']['description']}")
        output.append("\nUniform Indicators:")
        for uniform in rules['friends']['indicators']['uniforms']:
            output.append(f"  • {uniform['type']}: {uniform['description']}")
            output.append(f"    Insignia: {uniform['insignia']}")
        
        output.append("\nBehavioral Indicators:")
        for behavior in rules['friends']['indicators']['behavioral_indicators']:
            output.append(f"  • {behavior}")
        
        # Foes
        output.append("\n[FOES - Hostile Forces]")
        output.append(f"Description: {rules['foes']['description']}")
        output.append("\nUniform Indicators:")
        for uniform in rules['foes']['indicators']['uniforms']:
            output.append(f"  • {uniform['type']}: {uniform['description']}")
            output.append(f"    Insignia: {uniform['insignia']}")
        
        output.append("\nBehavioral Indicators:")
        for behavior in rules['foes']['indicators']['behavioral_indicators']:
            output.append(f"  • {behavior}")
        
        # Civilians
        output.append("\n[CIVILIANS - Non-Combatants]")
        output.append(f"Description: {rules['civilians']['description']}")
        output.append("\nAppearance Indicators:")
        for indicator in rules['civilians']['indicators']['appearance']:
            output.append(f"  • {indicator}")
        
        output.append("\nBehavioral Indicators:")
        for behavior in rules['civilians']['indicators']['behavioral_indicators']:
            output.append(f"  • {behavior}")
        
        output.append("\nContext Indicators:")
        for ctx in rules['civilians']['indicators']['context']:
            output.append(f"  • {ctx}")
        
        # Unknown Threats
        output.append("\n[UNKNOWN THREATS]")
        output.append(f"Description: {rules['unknown_threats']['description']}")
        
        output.append("\n  Subcategory: Armed Civilians")
        armed_civ = rules['unknown_threats']['subcategories']['armed_civilians']
        output.append(f"    {armed_civ['description']}")
        output.append(f"    Note: {armed_civ['note']}")
        
        output.append("\n  Subcategory: Mixed Indicators")
        mixed = rules['unknown_threats']['subcategories']['mixed_indicators']
        output.append(f"    {mixed['description']}")
        output.append("    Examples:")
        for example in mixed['examples']:
            output.append(f"      - {example}")
        
        output.append("\n  Subcategory: Insufficient Data")
        insufficient = rules['unknown_threats']['subcategories']['insufficient_data']
        output.append(f"    {insufficient['description']}")
        output.append("    Examples:")
        for example in insufficient['examples']:
            output.append(f"      - {example}")
        
        # Classification Decision Process
        output.extend([
            "\n" + "=" * 70,
            "CLASSIFICATION DECISION PROCESS:",
            "=" * 70,
        ])
        
        decision_process = rules['classification_decision_process']
        for step_key in sorted([k for k in decision_process.keys() if k.startswith('step_')]):
            output.append(f"  {decision_process[step_key]}")
        
        # Assessment Guidelines
        output.extend([
            "\n" + "=" * 70,
            "ASSESSMENT GUIDELINES:",
            "=" * 70,
            "\nDO:",
        ])
        for guideline in rules['assessment_guidelines']['do']:
            output.append(f"  ✓ {guideline}")
        
        output.append("\nDO NOT:")
        for guideline in rules['assessment_guidelines']['do_not']:
            output.append(f"  ✗ {guideline}")
        
        # Reference images (if available)
        if 'reference_images' in rules:
            output.extend([
                "\n" + "=" * 70,
                "VISUAL REFERENCE IMAGES AVAILABLE:",
                "=" * 70,
                "\nFor comparison with observed insignia/uniforms:",
            ])
            
            refs = rules['reference_images']
            
            if 'friends' in refs:
                output.append("\n[FRIEND INSIGNIA REFERENCES]:")
                for key, path in refs['friends'].items():
                    if isinstance(path, str):
                        output.append(f"  • {key}: {path}")
                    elif isinstance(path, list):
                        output.append(f"  • {key}:")
                        for item in path:
                            output.append(f"    - {item}")
            
            if 'foes' in refs:
                output.append("\n[FOE INSIGNIA REFERENCES]:")
                for key, path in refs['foes'].items():
                    if isinstance(path, list):
                        output.append(f"  • {key}:")
                        for item in path:
                            output.append(f"    - {item}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)