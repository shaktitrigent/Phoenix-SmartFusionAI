"""BDD test case generator (integrates SmartCaseAI logic)."""

import re
from typing import List, Optional
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
            output_format="gherkin",
            num_cases=num_cases,
            additional_files=context_files
        )
        
        # Parse the generated feature
        return self.parse_feature_content(feature_content)

