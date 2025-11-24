"""Tests for fusion mapper."""

import pytest
from core.fusion_mapper import FusionMapper
from core.utils.models import (
    BDDFeature,
    BDDScenario,
    BDDStep,
    StepType,
    LocatorDictionary,
    LocatorInfo,
    LocatorType,
    FusionConfig
)


class TestFusionMapper:
    """Test cases for FusionMapper."""
    
    def test_map_step_with_exact_match(self):
        """Test mapping a step with exact locator match."""
        # Create locator dictionary
        locator_dict = LocatorDictionary()
        locator_info = LocatorInfo(
            variable_name="self.user_name_input",
            locator_expression="page.locator('#username')",
            normalized_name="user_name",
            locator_type=LocatorType.PLAYWRIGHT
        )
        locator_dict.add_locator("user_name", locator_info)
        
        # Create step
        step = BDDStep(
            step_type=StepType.WHEN,
            text='I enter "user_name"',
            tokens=["user_name"],
            original_text='When I enter "user_name"'
        )
        
        # Map step
        mapper = FusionMapper()
        enhanced_step, mapping_result = mapper._map_step(step, locator_dict)
        
        assert mapping_result.matched is True
        assert mapping_result.locator_variable == "self.user_name_input"
        assert mapping_result.match_type == "exact"
        assert "${self.user_name_input}" in enhanced_step.text
    
    def test_map_feature(self):
        """Test mapping a complete feature."""
        # Create feature
        feature = BDDFeature(
            feature_name="Login Feature",
            scenarios=[
                BDDScenario(
                    name="Valid Login",
                    steps=[
                        BDDStep(
                            step_type=StepType.GIVEN,
                            text="I am on the login page",
                            tokens=[],
                            original_text="Given I am on the login page"
                        ),
                        BDDStep(
                            step_type=StepType.WHEN,
                            text='I enter "user_name"',
                            tokens=["user_name"],
                            original_text='When I enter "user_name"'
                        ),
                        BDDStep(
                            step_type=StepType.WHEN,
                            text='I enter "password"',
                            tokens=["password"],
                            original_text='When I enter "password"'
                        ),
                        BDDStep(
                            step_type=StepType.WHEN,
                            text='I click on "submit"',
                            tokens=["submit"],
                            original_text='When I click on "submit"'
                        )
                    ]
                )
            ]
        )
        
        # Create locator dictionary
        locator_dict = LocatorDictionary()
        for name, var_name in [("user_name", "self.user_name_input"),
                               ("password", "self.password_input"),
                               ("submit", "self.submit_button")]:
            locator_info = LocatorInfo(
                variable_name=var_name,
                locator_expression=f"page.locator('#{name}')",
                normalized_name=name,
                locator_type=LocatorType.PLAYWRIGHT
            )
            locator_dict.add_locator(name, locator_info)
        
        # Map feature
        mapper = FusionMapper()
        enhanced_feature, report = mapper.map_feature(feature, locator_dict)
        
        assert enhanced_feature.feature_name == "Login Feature"
        assert len(enhanced_feature.scenarios) == 1
        assert report.matched_steps >= 3  # At least 3 steps should match
        assert report.total_steps == 4

