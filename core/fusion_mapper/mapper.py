"""Fusion mapper that maps BDD steps to locator variables."""

import re
from typing import List, Dict, Optional, Tuple
from core.utils.models import (
    BDDFeature,
    BDDStep,
    LocatorDictionary,
    MappingResult,
    FusionReport,
    FusionConfig,
    StepType,
)


class FusionMapper:
    """Maps BDD steps to locator variables."""
    
    # Mapping patterns for different step types
    STEP_PATTERNS = {
        "input": [
            r'enter\s+(?:text\s+)?(?:into\s+)?["\']?(\w+)["\']?',
            r'fill\s+["\']?(\w+)["\']?',
            r'type\s+(?:in\s+)?(?:to\s+)?["\']?(\w+)["\']?',
            r'input\s+(?:text\s+)?(?:into\s+)?["\']?(\w+)["\']?',
        ],
        "click": [
            r'click\s+(?:on\s+)?["\']?(\w+)["\']?',
            r'press\s+["\']?(\w+)["\']?',
            r'tap\s+(?:on\s+)?["\']?(\w+)["\']?',
        ],
        "select": [
            r'select\s+["\']?(\w+)["\']?',
            r'choose\s+["\']?(\w+)["\']?',
        ],
        "assert": [
            r'see\s+["\']?(\w+)["\']?',
            r'verify\s+["\']?(\w+)["\']?',
            r'check\s+["\']?(\w+)["\']?',
        ],
    }
    
    def __init__(self, config: Optional[FusionConfig] = None):
        """Initialize the fusion mapper.
        
        Args:
            config: Fusion configuration
        """
        self.config = config or FusionConfig()
    
    def map_feature(
        self,
        feature: BDDFeature,
        locator_dict: LocatorDictionary
    ) -> Tuple[BDDFeature, FusionReport]:
        """Map a BDD feature to locator variables.
        
        Args:
            feature: BDD feature to map
            locator_dict: Dictionary of available locators
            
        Returns:
            Tuple of (enhanced_feature, fusion_report)
        """
        enhanced_feature = BDDFeature(
            feature_name=feature.feature_name,
            description=feature.description,
            tags=feature.tags.copy(),
            scenarios=[]
        )
        
        report = FusionReport(
            feature_name=feature.feature_name,
            total_steps=0,
            matched_steps=0,
            unmatched_steps=0,
            mappings=[],
            unmatched_tokens=[],
            warnings=[],
            validation_results={}
        )
        
        # Process each scenario
        for scenario in feature.scenarios:
            enhanced_scenario = self._map_scenario(scenario, locator_dict, report)
            enhanced_feature.scenarios.append(enhanced_scenario)
        
        # Calculate statistics
        report.total_steps = len(report.mappings)
        report.matched_steps = sum(1 for m in report.mappings if m.matched)
        report.unmatched_steps = report.total_steps - report.matched_steps
        
        # Collect unmatched tokens
        for mapping in report.mappings:
            if not mapping.matched and mapping.step.tokens:
                report.unmatched_tokens.extend(mapping.step.tokens)
        
        report.unmatched_tokens = list(set(report.unmatched_tokens))
        
        return enhanced_feature, report
    
    def _map_scenario(
        self,
        scenario,
        locator_dict: LocatorDictionary,
        report: FusionReport
    ) -> "BDDScenario":
        """Map a scenario's steps to locators.
        
        Args:
            scenario: BDD scenario
            locator_dict: Dictionary of available locators
            report: Fusion report to update
            
        Returns:
            Enhanced scenario with mapped steps
        """
        from core.utils.models import BDDScenario
        
        enhanced_scenario = BDDScenario(
            name=scenario.name,
            tags=scenario.tags.copy(),
            steps=[]
        )
        
        for step in scenario.steps:
            mapped_step, mapping_result = self._map_step(step, locator_dict)
            enhanced_scenario.steps.append(mapped_step)
            report.mappings.append(mapping_result)
        
        return enhanced_scenario
    
    def _map_step(
        self,
        step: BDDStep,
        locator_dict: LocatorDictionary
    ) -> Tuple[BDDStep, MappingResult]:
        """Map a single step to a locator variable.
        
        Args:
            step: BDD step to map
            locator_dict: Dictionary of available locators
            
        Returns:
            Tuple of (enhanced_step, mapping_result)
        """
        # Extract tokens from step text
        tokens = self._extract_tokens_from_step(step.text)
        
        # Try to match tokens to locators
        matched_locator = None
        match_type = None
        warning = None
        
        for token in tokens:
            # Try exact match first
            locator_info = locator_dict.get_locator(token)
            if locator_info:
                matched_locator = locator_info.variable_name
                match_type = "exact"
                break
            
            # Try partial match if enabled
            if self.config.enable_partial_matching:
                partial_match = locator_dict.find_partial_match(token)
                if partial_match:
                    locator_info = locator_dict.get_locator(partial_match)
                    matched_locator = locator_info.variable_name
                    match_type = "partial"
                    warning = f"Partial match: '{token}' -> '{partial_match}'"
                    break
        
        # Create enhanced step text
        enhanced_text = self._rewrite_step_text(step.text, matched_locator, tokens)
        
        # Create enhanced step
        enhanced_step = BDDStep(
            step_type=step.step_type,
            text=enhanced_text,
            tokens=tokens,
            mapped_locator=matched_locator,
            original_text=step.original_text
        )
        
        # Create mapping result
        mapping_result = MappingResult(
            step=step,
            matched=matched_locator is not None,
            locator_variable=matched_locator,
            match_type=match_type,
            warning=warning
        )
        
        # Add warning if no match found
        if not matched_locator and tokens:
            if self.config.strict_mode:
                warning = f"No locator found for tokens: {', '.join(tokens)}"
                mapping_result.warning = warning
        
        return enhanced_step, mapping_result
    
    def _extract_tokens_from_step(self, step_text: str) -> List[str]:
        """Extract tokens from step text.
        
        Args:
            step_text: Step text
            
        Returns:
            List of extracted tokens
        """
        tokens = []
        
        # Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', step_text)
        tokens.extend(quoted)
        
        # Extract tokens using patterns
        for pattern_type, patterns in self.STEP_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, step_text, re.IGNORECASE)
                tokens.extend(matches)
        
        # Normalize tokens
        tokens = [t.lower().strip() for t in tokens if t]
        
        # Remove duplicates
        tokens = list(set(tokens))
        
        return tokens
    
    def _rewrite_step_text(
        self,
        original_text: str,
        locator_variable: Optional[str],
        tokens: List[str]
    ) -> str:
        """Rewrite step text with locator variable.
        
        Args:
            original_text: Original step text
            locator_variable: Mapped locator variable (e.g., ${self.user_name_input})
            tokens: Extracted tokens
            
        Returns:
            Rewritten step text
        """
        if not locator_variable:
            return original_text
        
        # Replace tokens with locator variable
        enhanced_text = original_text
        
        for token in tokens:
            # Replace quoted tokens
            pattern = f'"{token}"'
            if pattern in enhanced_text:
                enhanced_text = enhanced_text.replace(pattern, f"${{{locator_variable}}}")
            else:
                # Replace unquoted tokens
                enhanced_text = re.sub(
                    rf'\b{re.escape(token)}\b',
                    f"${{{locator_variable}}}",
                    enhanced_text,
                    flags=re.IGNORECASE
                )
        
        return enhanced_text
    
    def generate_mapping_table(self, feature: BDDFeature, locator_dict: LocatorDictionary) -> Dict:
        """Generate a mapping table for traceability.
        
        Args:
            feature: BDD feature
            locator_dict: Locator dictionary
            
        Returns:
            Mapping table dictionary
        """
        mapping_table = {
            "feature": feature.feature_name,
            "scenarios": []
        }
        
        for scenario in feature.scenarios:
            scenario_mapping = {
                "scenario": scenario.name,
                "steps": []
            }
            
            for step in scenario.steps:
                tokens = self._extract_tokens_from_step(step.text)
                matched_locators = []
                
                for token in tokens:
                    locator_info = locator_dict.get_locator(token)
                    if locator_info:
                        matched_locators.append({
                            "token": token,
                            "locator_variable": locator_info.variable_name,
                            "locator_expression": locator_info.locator_expression
                        })
                
                scenario_mapping["steps"].append({
                    "step_type": step.step_type.value,
                    "step_text": step.text,
                    "tokens": tokens,
                    "matched_locators": matched_locators
                })
            
            mapping_table["scenarios"].append(scenario_mapping)
        
        return mapping_table

