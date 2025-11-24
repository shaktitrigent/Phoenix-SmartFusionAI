"""Pydantic models for SmartFusionAI data structures."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    """BDD step types."""
    GIVEN = "Given"
    WHEN = "When"
    THEN = "Then"
    AND = "And"
    BUT = "But"


class LocatorType(str, Enum):
    """Locator types."""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"


class LocatorInfo(BaseModel):
    """Information about a locator."""
    variable_name: str = Field(..., description="Variable name (e.g., self.user_name_input)")
    locator_expression: str = Field(..., description="Locator expression (e.g., page.locator('#username'))")
    normalized_name: str = Field(..., description="Normalized element name (e.g., user_name)")
    locator_type: LocatorType = Field(default=LocatorType.PLAYWRIGHT)


class LocatorDictionary(BaseModel):
    """Dictionary mapping normalized names to locator info."""
    locators: Dict[str, LocatorInfo] = Field(default_factory=dict)
    
    def add_locator(self, normalized_name: str, locator_info: LocatorInfo):
        """Add a locator to the dictionary."""
        self.locators[normalized_name] = locator_info
    
    def get_locator(self, normalized_name: str) -> Optional[LocatorInfo]:
        """Get locator by normalized name."""
        return self.locators.get(normalized_name)
    
    def find_partial_match(self, token: str) -> Optional[str]:
        """Find partial match for a token."""
        token_lower = token.lower()
        for name, locator_info in self.locators.items():
            if token_lower in name.lower() or name.lower() in token_lower:
                return name
        return None


class BDDStep(BaseModel):
    """A BDD step."""
    step_type: StepType
    text: str = Field(..., description="Step text")
    tokens: List[str] = Field(default_factory=list, description="Extracted tokens from step")
    mapped_locator: Optional[str] = Field(default=None, description="Mapped locator variable")
    original_text: str = Field(..., description="Original step text before mapping")


class BDDScenario(BaseModel):
    """A BDD scenario."""
    name: str
    steps: List[BDDStep] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class BDDFeature(BaseModel):
    """A BDD feature file."""
    feature_name: str
    description: str = ""
    scenarios: List[BDDScenario] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class MappingResult(BaseModel):
    """Result of mapping a step to a locator."""
    step: BDDStep
    matched: bool
    locator_variable: Optional[str] = None
    match_type: Optional[str] = None  # "exact", "partial", "none"
    warning: Optional[str] = None


class FusionReport(BaseModel):
    """Fusion mapping report."""
    feature_name: str
    total_steps: int
    matched_steps: int
    unmatched_steps: int
    mappings: List[MappingResult] = Field(default_factory=list)
    unmatched_tokens: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validation_results: Dict[str, Any] = Field(default_factory=dict)


class FusionConfig(BaseModel):
    """Configuration for Fusion engine."""
    framework: LocatorType = LocatorType.PLAYWRIGHT
    enable_partial_matching: bool = True
    strict_mode: bool = False
    output_format: str = "both"  # "feature", "steps", "both"

