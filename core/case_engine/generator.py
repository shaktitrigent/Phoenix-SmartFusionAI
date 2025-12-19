"""BDD test case generator (integrates SmartCaseAI logic)."""

import re
import json
from typing import List, Optional, Union
from pathlib import Path

# External library import (required dependency)
try:
    from phoenix_smartcaseai import StoryBDDGenerator  # type: ignore
except ImportError:
    StoryBDDGenerator = None

from core.utils.models import BDDStep, BDDScenario, BDDFeature, StepType


class BDDGenerator:
    """Generator for BDD test cases from user stories."""
    
    def __init__(self):
        """Initialize the BDD generator."""
        pass
    
    def parse_feature_file(self, file_path: str) -> BDDFeature:
        """Parse an existing .feature file.
        
        Args:
            file_path: Path to .feature file
            
        Returns:
            BDDFeature object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_feature_content(content)
    
    def parse_feature_content(self, content: str) -> BDDFeature:
        """Parse feature file content.
        
        Args:
            content: Feature file content as string
            
        Returns:
            BDDFeature object
        """
        lines = content.split('\n')
        feature = BDDFeature(feature_name="", description="")
        current_scenario = None
        tags = []
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Parse tags
            if line.startswith('@'):
                tags = [tag.strip('@') for tag in line.split()]
                continue
            
            # Parse Feature
            if line.startswith('Feature:'):
                feature.feature_name = line.replace('Feature:', '').strip()
                feature.tags = tags.copy()
                tags = []
                continue
            
            # Parse Scenario
            if line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                if current_scenario:
                    feature.scenarios.append(current_scenario)
                scenario_name = line.replace('Scenario:', '').replace('Scenario Outline:', '').strip()
                current_scenario = BDDScenario(name=scenario_name, tags=tags.copy())
                tags = []
                continue
            
            # Parse Background
            if line.startswith('Background:'):
                if current_scenario:
                    feature.scenarios.append(current_scenario)
                current_scenario = BDDScenario(name="Background", tags=[])
                continue
            
            # Parse Steps
            if current_scenario:
                step = self._parse_step(line)
                if step:
                    current_scenario.steps.append(step)
        
        if current_scenario:
            feature.scenarios.append(current_scenario)
        
        return feature
    
    def _parse_step(self, line: str) -> Optional[BDDStep]:
        """Parse a single step line.
        
        Args:
            line: Step line (e.g., "Given I am on the login page")
            
        Returns:
            BDDStep object or None
        """
        line = line.strip()
        if not line:
            return None
        
        # Determine step type
        step_type = None
        for st in StepType:
            if line.startswith(st.value):
                step_type = st
                text = line[len(st.value):].strip()
                break
        
        if not step_type:
            return None
        
        # Extract tokens (quoted strings, element names, etc.)
        tokens = self._extract_tokens(text)
        
        return BDDStep(
            step_type=step_type,
            text=text,
            tokens=tokens,
            original_text=line
        )
    
    def _extract_tokens(self, text: str) -> List[str]:
        """Extract tokens from step text.
        
        Tokens are typically:
        - Quoted strings: "user_name", "password"
        - Element names after keywords: enter "field", click on "button"
        
        Args:
            text: Step text
            
        Returns:
            List of extracted tokens
        """
        tokens = []
        
        # Extract quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        tokens.extend(quoted)
        
        # Extract element names after common keywords
        patterns = [
            r'enter\s+["\']?(\w+)["\']?',
            r'click\s+(?:on\s+)?["\']?(\w+)["\']?',
            r'select\s+["\']?(\w+)["\']?',
            r'fill\s+["\']?(\w+)["\']?',
            r'type\s+(?:in\s+)?["\']?(\w+)["\']?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tokens.extend(matches)
        
        # Remove duplicates and normalize
        tokens = list(set([t.lower() for t in tokens if t]))
        
        return tokens
    
    def generate_from_story(self, user_story: str, num_cases: int = 5, llm_provider: str = "openai", context_files: Optional[List[str]] = None) -> BDDFeature:
        """Generate BDD feature from user story using SmartCaseAI.
        
        This method uses SmartCaseAI for LLM-powered generation.
        SmartCaseAI is required - no fallback.
        
        Args:
            user_story: User story text
            num_cases: Number of test cases to generate
            llm_provider: LLM provider (openai, gemini, claude)
            context_files: Optional list of context file paths
            
        Returns:
            BDDFeature object
            
        Raises:
            ImportError: If SmartCaseAI is not installed
        """
        # Use SmartCaseAI directly - it's required
        if StoryBDDGenerator is None:
            raise ImportError(
                "phoenix-smartcaseai package not found. Please install it: "
                "pip install phoenix-smartcaseai"
            )
        
        generator = StoryBDDGenerator(llm_provider=llm_provider)
        feature_content = generator.generate_test_cases(
            user_story=user_story,
            output_format="bdd",
            num_cases=num_cases,
            additional_files=context_files
        )
        
        # SmartCaseAI returns JSON when output_format="bdd", need to parse it
        if isinstance(feature_content, str):
            # Try to parse as JSON first
            try:
                import json
                feature_data = json.loads(feature_content)
                return self._parse_json_bdd(feature_data)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, treat as Gherkin text
                return self.parse_feature_content(feature_content)
        elif isinstance(feature_content, (list, dict)):
            # Already parsed JSON
            return self._parse_json_bdd(feature_content)
        else:
            # Fallback to string parsing
            return self.parse_feature_content(str(feature_content))
    
    def _parse_json_bdd(self, data: Union[list, dict]) -> BDDFeature:
        """Parse JSON BDD format from SmartCaseAI.
        
        Args:
            data: JSON data (list or dict) from SmartCaseAI
            
        Returns:
            BDDFeature object
        """
        from core.utils.models import BDDFeature, BDDScenario, BDDStep, StepType
        
        # Handle list format (multiple scenarios)
        if isinstance(data, list):
            if not data:
                return BDDFeature(feature_name="", description="")
            # Use first item for feature name, process all for scenarios
            first_item = data[0]
            feature_name = first_item.get("feature", "Generated Feature")
            scenarios = []
            
            for item in data:
                scenario_name = item.get("scenario", "Generated Scenario")
                scenario = BDDScenario(name=scenario_name, tags=[])
                
                # Parse Given steps
                for step_text in item.get("given", []):
                    if isinstance(step_text, str):
                        scenario.steps.append(BDDStep(
                            step_type=StepType.GIVEN,
                            text=step_text,
                            tokens=self._extract_tokens(step_text),
                            original_text=f"Given {step_text}"
                        ))
                
                # Parse When steps
                for step_text in item.get("when", []):
                    if isinstance(step_text, str):
                        scenario.steps.append(BDDStep(
                            step_type=StepType.WHEN,
                            text=step_text,
                            tokens=self._extract_tokens(step_text),
                            original_text=f"When {step_text}"
                        ))
                
                # Parse Then steps
                for step_text in item.get("then", []):
                    if isinstance(step_text, str):
                        scenario.steps.append(BDDStep(
                            step_type=StepType.THEN,
                            text=step_text,
                            tokens=self._extract_tokens(step_text),
                            original_text=f"Then {step_text}"
                        ))
                
                scenarios.append(scenario)
            
            return BDDFeature(feature_name=feature_name, description="", scenarios=scenarios)
        
        # Handle dict format (single scenario)
        elif isinstance(data, dict):
            feature_name = data.get("feature", "Generated Feature")
            scenario_name = data.get("scenario", "Generated Scenario")
            scenario = BDDScenario(name=scenario_name, tags=[])
            
            # Parse Given steps
            for step_text in data.get("given", []):
                if isinstance(step_text, str):
                    scenario.steps.append(BDDStep(
                        step_type=StepType.GIVEN,
                        text=step_text,
                        tokens=self._extract_tokens(step_text),
                        original_text=f"Given {step_text}"
                    ))
            
            # Parse When steps
            for step_text in data.get("when", []):
                if isinstance(step_text, str):
                    scenario.steps.append(BDDStep(
                        step_type=StepType.WHEN,
                        text=step_text,
                        tokens=self._extract_tokens(step_text),
                        original_text=f"When {step_text}"
                    ))
            
            # Parse Then steps
            for step_text in data.get("then", []):
                if isinstance(step_text, str):
                    scenario.steps.append(BDDStep(
                        step_type=StepType.THEN,
                        text=step_text,
                        tokens=self._extract_tokens(step_text),
                        original_text=f"Then {step_text}"
                    ))
            
            return BDDFeature(feature_name=feature_name, description="", scenarios=[scenario])
        
        else:
            raise ValueError(f"Unexpected data type for JSON BDD: {type(data)}")

