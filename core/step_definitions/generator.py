"""Generator for Python step definition files."""

import re
from typing import List, Dict
from core.utils.models import BDDFeature, LocatorType, StepType


class StepDefinitionGenerator:
    """Generates Python step definition code."""
    
    def __init__(self, framework: LocatorType = LocatorType.PLAYWRIGHT):
        """Initialize the generator.
        
        Args:
            framework: Framework type (Playwright or Selenium)
        """
        self.framework = framework
    
    def generate(self, feature: BDDFeature) -> str:
        """Generate step definition file content.
        
        Args:
            feature: BDD feature with mapped locators
            
        Returns:
            Python code as string
        """
        if self.framework == LocatorType.PLAYWRIGHT:
            return self._generate_playwright_steps(feature)
        else:
            return self._generate_selenium_steps(feature)
    
    def _generate_playwright_steps(self, feature: BDDFeature) -> str:
        """Generate Playwright step definitions for pytest-bdd.
        
        Args:
            feature: BDD feature
            
        Returns:
            Python code
        """
        code_lines = [
            '"""Auto-generated step definitions for Playwright using pytest-bdd."""',
            '',
            'import pytest',
            'from pytest_bdd import given, when, then, parsers',
            'from playwright.sync_api import Page, expect, sync_playwright',
            '',
            '',
            '# ===== Fixtures =====',
            '',
            '@pytest.fixture(scope="session")',
            'def playwright():',
            '    """Initialize Playwright."""',
            '    with sync_playwright() as p:',
            '        yield p',
            '',
            '',
            '@pytest.fixture(scope="session")',
            'def browser(playwright):',
            '    """Get browser instance."""',
            '    browser = playwright.chromium.launch(headless=True)',
            '    yield browser',
            '    browser.close()',
            '',
            '',
            '@pytest.fixture',
            'def page(browser):',
            '    """Get Playwright page fixture."""',
            '    page = browser.new_page()',
            '    yield page',
            '    page.close()',
            '',
            '',
            '# ===== Given Steps =====',
            ''
        ]
        
        # Collect unique step patterns
        step_patterns = self._extract_step_patterns(feature)
        
        # Generate step definitions by type
        code_lines.extend(self._generate_given_steps(step_patterns.get('given', [])))
        code_lines.extend(self._generate_when_steps(step_patterns.get('when', [])))
        code_lines.extend(self._generate_then_steps(step_patterns.get('then', [])))
        code_lines.extend(self._generate_and_steps(step_patterns.get('and', [])))
        
        return '\n'.join(code_lines)
    
    def _generate_selenium_steps(self, feature: BDDFeature) -> str:
        """Generate Selenium step definitions for pytest-bdd.
        
        Args:
            feature: BDD feature
            
        Returns:
            Python code
        """
        code_lines = [
            '"""Auto-generated step definitions for Selenium using pytest-bdd."""',
            '',
            'import pytest',
            'from pytest_bdd import given, when, then, parsers',
            'from selenium.webdriver.common.by import By',
            'from selenium.webdriver.support.ui import WebDriverWait',
            'from selenium.webdriver.support import expected_conditions as EC',
            '',
            '',
            '# ===== Fixtures =====',
            '',
            '@pytest.fixture',
            'def driver(browser):',
            '    """Get Selenium WebDriver fixture."""',
            '    # Initialize WebDriver',
            '    # This should be customized based on your setup',
            '    return browser',
            '',
            '',
            '# ===== Given Steps =====',
            ''
        ]
        
        # Collect unique step patterns
        step_patterns = self._extract_step_patterns(feature)
        
        # Generate step definitions by type
        code_lines.extend(self._generate_given_steps_selenium(step_patterns.get('given', [])))
        code_lines.extend(self._generate_when_steps_selenium(step_patterns.get('when', [])))
        code_lines.extend(self._generate_then_steps_selenium(step_patterns.get('then', [])))
        code_lines.extend(self._generate_and_steps_selenium(step_patterns.get('and', [])))
        
        return '\n'.join(code_lines)
    
    def _extract_step_patterns(self, feature: BDDFeature) -> Dict[str, List[str]]:
        """Extract unique step patterns from feature.
        
        Args:
            feature: BDD feature
            
        Returns:
            Dictionary of step patterns by type
        """
        patterns = {
            'given': [],
            'when': [],
            'then': [],
            'and': []
        }
        
        for scenario in feature.scenarios:
            for step in scenario.steps:
                step_type = step.step_type.value.lower()
                pattern = self._create_step_pattern(step.text)
                
                if pattern not in patterns[step_type]:
                    patterns[step_type].append(pattern)
        
        return patterns
    
    def _create_step_pattern(self, step_text: str) -> str:
        """Create a regex pattern from step text.
        
        Args:
            step_text: Step text
            
        Returns:
            Regex pattern string
        """
        # Replace locator variables with regex groups
        pattern = step_text
        
        # Replace ${...} with regex group that matches any non-whitespace
        # Use [^\\s]+ (double backslash) so it becomes [^\s]+ in the final string
        pattern = re.sub(r'\$\{[^}]+\}', r'(?P<locator>[^\\s]+)', pattern)
        
        # Replace quoted strings with regex groups
        pattern = re.sub(r'"([^"]+)"', r'"(?P<value>[^"]+)"', pattern)
        
        # Escape special regex characters but keep our groups
        # This is simplified - in production, more sophisticated pattern generation
        
        return pattern
    
    def _generate_given_steps(self, patterns: List[str]) -> List[str]:
        """Generate Given step definitions for Playwright with pytest-bdd."""
        lines = []
        
        for pattern in patterns:
            if 'on the' in pattern.lower() or 'navigate' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@given(parsers.re(r"""^{escaped}$"""))',
                    'def step_given_navigate(page):',
                    '    """Navigate to a page."""',
                    '    # Implement navigation logic',
                    '    # Example: page.goto("https://example.com/login")',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_when_steps(self, patterns: List[str]) -> List[str]:
        """Generate When step definitions for Playwright."""
        lines = [
            '',
            '# ===== When Steps =====',
            ''
        ]
        
        for pattern in patterns:
            if 'enter' in pattern.lower() or 'fill' in pattern.lower() or 'type' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                # Use triple quotes to avoid escaping issues
                lines.extend([
                    f'@when(parsers.re(r"""^{escaped}$"""))',
                    'def step_when_enter_text(page, locator=None, value=None):',
                    '    """Enter text into a field."""',
                    '    if locator:',
                    '        # Extract locator variable',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            # Get element from page object',
                    '            # element = getattr(page, locator_var, None)',
                    '            # if element and value:',
                    '            #     element.fill(value)',
                    '            # For now, use direct locator',
                    '            page.locator(f"#{locator_var}").fill(value or "test_value")',
                    '    pass',
                    '',
                ])
            elif 'click' in pattern.lower() or 'press' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@when(parsers.re(r"""^{escaped}$"""))',
                    'def step_when_click(page, locator=None):',
                    '    """Click on an element."""',
                    '    if locator:',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            # Get element from page object',
                    '            # element = getattr(page, locator_var, None)',
                    '            # if element:',
                    '            #     element.click()',
                    '            # For now, use direct locator',
                    '            page.locator(f"#{locator_var}").click()',
                    '    pass',
                    '',
                ])
            elif 'select' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@when(parsers.re(r"""^{escaped}$"""))',
                    'def step_when_select(page, locator=None, value=None):',
                    '    """Select an option."""',
                    '    if locator and value:',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            # Get element from page object',
                    '            # element = getattr(page, locator_var, None)',
                    '            # if element:',
                    '            #     element.select_option(value)',
                    '            # For now, use direct locator',
                    '            page.locator(f"#{locator_var}").select_option(value)',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_then_steps(self, patterns: List[str]) -> List[str]:
        """Generate Then step definitions for Playwright."""
        lines = [
            '',
            '# ===== Then Steps =====',
            ''
        ]
        
        for pattern in patterns:
            if 'see' in pattern.lower() or 'verify' in pattern.lower() or 'check' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@then(parsers.re(r"""^{escaped}$"""))',
                    'def step_then_verify(page, locator=None, value=None):',
                    '    """Verify an element or text is visible."""',
                    '    if locator and locator.startswith("${") and locator.endswith("}"):',
                    '        locator_var = locator[2:-1].split(".")[-1]',
                    '        # Get element from page object',
                    '        # element = getattr(page, locator_var, None)',
                    '        # if element:',
                    '        #     expect(element).to_be_visible()',
                    '        # For now, use direct locator',
                    '        expect(page.locator(f"#{locator_var}")).to_be_visible()',
                    '    elif value:',
                    '        # Check for text content',
                    '        expect(page.locator(f"text={value}")).to_be_visible()',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_and_steps(self, patterns: List[str]) -> List[str]:
        """Generate And step definitions for Playwright with pytest-bdd."""
        lines = [
            '',
            '# ===== And Steps =====',
            '',
            '# Note: pytest-bdd handles "And" steps automatically by reusing',
            '# the same step definitions. No separate handler needed.',
            ''
        ]
        
        return lines
    
    def _generate_given_steps_selenium(self, patterns: List[str]) -> List[str]:
        """Generate Given step definitions for Selenium with pytest-bdd."""
        lines = []
        
        for pattern in patterns:
            if 'on the' in pattern.lower() or 'navigate' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@given(parsers.re(r"""^{escaped}$"""))',
                    'def step_given_navigate(driver):',
                    '    """Navigate to a page."""',
                    '    # Implement navigation logic',
                    '    # Example: driver.get("https://example.com/login")',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_when_steps_selenium(self, patterns: List[str]) -> List[str]:
        """Generate When step definitions for Selenium."""
        lines = [
            '',
            '# ===== When Steps =====',
            ''
        ]
        
        for pattern in patterns:
            if 'enter' in pattern.lower() or 'fill' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@when(parsers.re(r"""^{escaped}$"""))',
                    'def step_when_enter_text(driver, locator=None, value=None):',
                    '    """Enter text into a field."""',
                    '    if locator:',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            element = driver.find_element(By.ID, locator_var)',
                    '            if element and value:',
                    '                element.send_keys(value)',
                    '    pass',
                    '',
                ])
            elif 'click' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@when(parsers.re(r"""^{escaped}$"""))',
                    'def step_when_click(driver, locator=None):',
                    '    """Click on an element."""',
                    '    if locator:',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            element = driver.find_element(By.ID, locator_var)',
                    '            if element:',
                    '                element.click()',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_then_steps_selenium(self, patterns: List[str]) -> List[str]:
        """Generate Then step definitions for Selenium."""
        lines = [
            '',
            '# ===== Then Steps =====',
            ''
        ]
        
        for pattern in patterns:
            if 'see' in pattern.lower() or 'verify' in pattern.lower():
                escaped = self._escape_pattern(pattern)
                lines.extend([
                    f'@then(parsers.re(r"""^{escaped}$"""))',
                    'def step_then_verify(driver, locator=None, value=None):',
                    '    """Verify an element or text is visible."""',
                    '    if locator:',
                    '        if locator.startswith("${") and locator.endswith("}"):',
                    '            locator_var = locator[2:-1].split(".")[-1]',
                    '            element = driver.find_element(By.ID, locator_var)',
                    '            assert element.is_displayed()',
                    '    elif value:',
                    '        assert value in driver.page_source',
                    '    pass',
                    '',
                ])
        
        return lines
    
    def _generate_and_steps_selenium(self, patterns: List[str]) -> List[str]:
        """Generate And step definitions for Selenium with pytest-bdd."""
        return self._generate_and_steps(patterns)
    
    def _escape_pattern(self, pattern: str) -> str:
        """Escape special characters in pattern for regex.
        
        Args:
            pattern: Pattern string (may already contain regex groups from _create_step_pattern)
            
        Returns:
            Escaped pattern
        """
        # Check if pattern already has regex groups (from _create_step_pattern)
        # If it has (?P<...>), we need to preserve those groups
        if '(?P<' in pattern:
            # Pattern already has regex groups, just escape special chars around them
            # Replace regex groups with placeholders temporarily
            pattern = re.sub(r'\(\?P<(\w+)>([^)]+)\)', r'__REGEX_GROUP_\1__', pattern)
            pattern = re.sub(r'"\(\?P<(\w+)>([^)]+)\)"', r'__QUOTED_GROUP_\1__', pattern)
            
            # Escape special regex characters (but not our placeholders)
            pattern = re.sub(r'([.*+?^$()|[\]\\])', r'\\\1', pattern)
            
            # Restore regex groups (they're already properly formatted)
            for group_name in ['locator', 'value']:
                pattern = pattern.replace(f'__REGEX_GROUP_{group_name}__', f'(?P<{group_name}>[^\\s]+)')
                pattern = pattern.replace(f'__QUOTED_GROUP_{group_name}__', f'"(?P<{group_name}>[^"]+)"')
        else:
            # Pattern has ${...} format, convert to regex groups
            pattern = re.sub(r'\$\{([^}]+)\}', r'__LOCATOR_PLACEHOLDER__', pattern)
            pattern = re.sub(r'"([^"]+)"', r'__VALUE_PLACEHOLDER__', pattern)
            
            # Escape special regex characters
            pattern = re.sub(r'([.*+?^$()|[\]\\])', r'\\\1', pattern)
            
            # Restore with regex groups and ${} format
            pattern = pattern.replace('__LOCATOR_PLACEHOLDER__', r'\$\{(?P<locator>[^\s]+)\}')
            pattern = pattern.replace('__VALUE_PLACEHOLDER__', r'"(?P<value>[^"]+)"')
        
        return pattern

