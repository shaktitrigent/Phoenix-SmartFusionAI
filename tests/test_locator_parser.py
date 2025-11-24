"""Tests for locator parser."""

import pytest
import json
import tempfile
from pathlib import Path
from core.locator_engine import LocatorParser
from core.utils.models import LocatorType


class TestLocatorParser:
    """Test cases for LocatorParser."""
    
    def test_parse_locators_json(self):
        """Test parsing locators.json file."""
        # Create temporary JSON file
        locators_data = {
            "user_name": {
                "variable": "self.user_name_input",
                "locator": "page.locator('#username')"
            },
            "password": {
                "variable": "self.password_input",
                "locator": "page.locator('#password')"
            },
            "submit": {
                "variable": "self.submit_button",
                "locator": "page.locator('button[type=submit]')"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(locators_data, f)
            temp_path = f.name
        
        try:
            parser = LocatorParser(LocatorType.PLAYWRIGHT)
            dictionary = parser.parse_locators_json(temp_path)
            
            assert len(dictionary.locators) == 3
            assert "user_name" in dictionary.locators
            assert dictionary.locators["user_name"].variable_name == "self.user_name_input"
            assert dictionary.locators["user_name"].locator_expression == "page.locator('#username')"
        finally:
            Path(temp_path).unlink()
    
    def test_normalize_name(self):
        """Test name normalization."""
        parser = LocatorParser()
        
        assert parser._normalize_name("user_name_input") == "user_name"
        assert parser._normalize_name("submit_button") == "submit"
        assert parser._normalize_name("loginForm") == "login_form"
    
    def test_get_locator(self):
        """Test getting locator from dictionary."""
        parser = LocatorParser()
        dictionary = parser.get_dictionary()
        
        from core.utils.models import LocatorInfo
        
        locator_info = LocatorInfo(
            variable_name="self.user_name_input",
            locator_expression="page.locator('#username')",
            normalized_name="user_name"
        )
        dictionary.add_locator("user_name", locator_info)
        
        retrieved = dictionary.get_locator("user_name")
        assert retrieved is not None
        assert retrieved.variable_name == "self.user_name_input"
        
        assert dictionary.get_locator("nonexistent") is None

