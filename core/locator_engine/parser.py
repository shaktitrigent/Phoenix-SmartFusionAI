"""Parser for extracting locators from page.py or locators.json files."""

import re
import json
import ast
from pathlib import Path
from typing import Dict, Optional, List
from core.utils.models import LocatorInfo, LocatorDictionary, LocatorType


class LocatorParser:
    """Parser for extracting locators from various formats."""
    
    def __init__(self, locator_type: LocatorType = LocatorType.PLAYWRIGHT):
        """Initialize the parser.
        
        Args:
            locator_type: Type of locator framework (Playwright or Selenium)
        """
        self.locator_type = locator_type
        self.dictionary = LocatorDictionary()
    
    def parse_page_py(self, file_path: str) -> LocatorDictionary:
        """Parse a page.py file and extract locators.
        
        Args:
            file_path: Path to page.py file
            
        Returns:
            LocatorDictionary with extracted locators
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse Python AST
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Look for assignments like: self.user_name_input = page.locator(...)
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        var_name = f"self.{target.attr}"
                        normalized_name = self._normalize_name(target.attr)
                        
                        # Extract locator expression
                        try:
                            if hasattr(ast, 'unparse'):
                                locator_expr = ast.unparse(node.value)
                            else:
                                # Fallback for Python < 3.9
                                import astor
                                try:
                                    locator_expr = astor.to_source(node.value).strip()
                                except ImportError:
                                    locator_expr = self._extract_locator_expr(node.value, content)
                        except Exception:
                            locator_expr = self._extract_locator_expr(node.value, content)
                        
                        locator_info = LocatorInfo(
                            variable_name=var_name,
                            locator_expression=locator_expr,
                            normalized_name=normalized_name,
                            locator_type=self.locator_type
                        )
                        
                        self.dictionary.add_locator(normalized_name, locator_info)
        
        return self.dictionary
    
    def parse_locators_json(self, file_path: str) -> LocatorDictionary:
        """Parse a locators.json file and extract locators.
        
        Supports both SmartLocatorAI format and simple format.
        SmartLocatorAI format: {"locators": [...], "metadata": {...}}
        Simple format: {"user_name": {"variable": "...", "locator": "..."}}
        
        Args:
            file_path: Path to locators.json file
            
        Returns:
            LocatorDictionary with extracted locators
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if this is SmartLocatorAI format (has "locators" array)
        if isinstance(data, dict) and "locators" in data:
            # SmartLocatorAI format - parse from locators array
            for locator_entry in data.get("locators", []):
                # Extract from SmartLocatorAI format
                custom_name = locator_entry.get("custom_name", "")
                locator_value = locator_entry.get("locator_value", "")
                locator_type_str = locator_entry.get("locator_type", "CSS Selector")
                
                # Normalize the name
                normalized_name = self._normalize_name(custom_name) if custom_name else ""
                if not normalized_name:
                    continue
                
                # Create variable name from custom_name
                var_name = f"self.{self._to_snake_case(custom_name)}"
                
                # Build locator expression based on type
                if "Role" in locator_type_str or "Text" in locator_type_str:
                    # Playwright role/text locator
                    locator_expr = f"page.get_by_role('{locator_value}')" if "Role" in locator_type_str else f"page.get_by_text('{locator_value}')"
                else:
                    # CSS or XPath
                    locator_expr = f"page.locator('{locator_value}')"
                
                locator_info = LocatorInfo(
                    variable_name=var_name,
                    locator_expression=locator_expr,
                    normalized_name=normalized_name,
                    locator_type=self.locator_type
                )
                
                self.dictionary.add_locator(normalized_name, locator_info)
        else:
            # Simple format - handle legacy structure
            for key, value in data.items():
                normalized_name = self._normalize_name(key)
                
                if isinstance(value, dict):
                    # Structure: {"user_name": {"variable": "self.user_name_input", "locator": "..."}}
                    var_name = value.get("variable", f"self.{key}")
                    locator_expr = value.get("locator", value.get("expression", str(value)))
                elif isinstance(value, str):
                    # Structure: {"user_name": "page.locator('#username')"}
                    var_name = f"self.{key}"
                    locator_expr = value
                else:
                    continue
                
                locator_info = LocatorInfo(
                    variable_name=var_name,
                    locator_expression=locator_expr,
                    normalized_name=normalized_name,
                    locator_type=self.locator_type
                )
                
                self.dictionary.add_locator(normalized_name, locator_info)
        
        return self.dictionary
    
    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case."""
        # Remove special characters and split
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        # Convert camelCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        # Clean up
        name = re.sub(r'_+', '_', name).strip('_')
        return name
    
    def parse(self, file_path: str) -> LocatorDictionary:
        """Parse a locator file (auto-detect format).
        
        Args:
            file_path: Path to locator file (.py or .json)
            
        Returns:
            LocatorDictionary with extracted locators
        """
        path = Path(file_path)
        
        if path.suffix == '.py':
            return self.parse_page_py(file_path)
        elif path.suffix == '.json':
            return self.parse_locators_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a variable name to a standard format.
        
        Examples:
            user_name_input -> user_name
            submit_button -> submit
            loginForm -> login_form
        """
        # Remove common suffixes
        suffixes = ['_input', '_button', '_link', '_field', '_element', '_selector', '_locator']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        
        # Convert camelCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        
        # Clean up
        name = name.replace('__', '_').strip('_')
        
        return name
    
    def _extract_locator_expr(self, node: ast.AST, source: str) -> str:
        """Extract locator expression from AST node using source code."""
        # Fallback method if ast.unparse is not available
        if isinstance(node, ast.Call):
            # Try to reconstruct the call
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
                if hasattr(node.func, 'value'):
                    if isinstance(node.func.value, ast.Name):
                        obj_name = node.func.value.id
                        return f"{obj_name}.{func_name}(...)"
        return "unknown_locator"
    
    def get_dictionary(self) -> LocatorDictionary:
        """Get the current locator dictionary."""
        return self.dictionary

