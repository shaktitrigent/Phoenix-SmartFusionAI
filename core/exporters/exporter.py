"""Exporter for generating output files."""

import json
from pathlib import Path
from typing import Optional
from core.utils.models import BDDFeature, FusionReport, LocatorType


class OutputExporter:
    """Exports enhanced features, step definitions, and reports."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the exporter.
        
        Args:
            output_dir: Base output directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "merged_feature_files").mkdir(exist_ok=True)
        (self.output_dir / "python_tests").mkdir(exist_ok=True)
        (self.output_dir / "fusion_reports").mkdir(exist_ok=True)
    
    def export_feature(
        self,
        feature: BDDFeature,
        filename: Optional[str] = None
    ) -> Path:
        """Export enhanced feature file.
        
        Args:
            feature: Enhanced BDD feature
            filename: Output filename (default: feature_name.feature)
            
        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"{self._sanitize_filename(feature.feature_name)}.feature"
        
        output_path = self.output_dir / "merged_feature_files" / filename
        
        content = self._generate_feature_content(feature)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def export_step_definitions(
        self,
        step_definitions: str,
        feature_name: str,
        framework: LocatorType = LocatorType.PLAYWRIGHT
    ) -> Path:
        """Export step definition file.
        
        Args:
            step_definitions: Step definition code
            feature_name: Feature name
            framework: Framework type
            
        Returns:
            Path to exported file
        """
        filename = f"test_{self._sanitize_filename(feature_name)}_steps.py"
        output_path = self.output_dir / "python_tests" / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(step_definitions)
        
        return output_path
    
    def export_fusion_report(
        self,
        report: FusionReport,
        filename: Optional[str] = None
    ) -> Path:
        """Export fusion mapping report.
        
        Args:
            report: Fusion report
            filename: Output filename (default: feature_name_fusion_report.json)
            
        Returns:
            Path to exported file
        """
        if not filename:
            filename = f"{self._sanitize_filename(report.feature_name)}_fusion_report.json"
        
        output_path = self.output_dir / "fusion_reports" / filename
        
        # Convert to dict for JSON serialization
        report_dict = report.model_dump()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_mapping_table(
        self,
        mapping_table: dict,
        feature_name: str
    ) -> Path:
        """Export traceability mapping table.
        
        Args:
            mapping_table: Mapping table dictionary
            feature_name: Feature name
            
        Returns:
            Path to exported file
        """
        filename = f"{self._sanitize_filename(feature_name)}_mapping_table.json"
        output_path = self.output_dir / "fusion_reports" / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_table, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _generate_feature_content(self, feature: BDDFeature) -> str:
        """Generate Gherkin feature file content.
        
        Args:
            feature: BDD feature
            
        Returns:
            Feature file content
        """
        lines = []
        
        # Add tags
        if feature.tags:
            lines.append(' '.join(f'@{tag}' for tag in feature.tags))
        
        # Add feature header
        lines.append(f"Feature: {feature.feature_name}")
        
        if feature.description:
            lines.append(f"  {feature.description}")
        
        lines.append("")
        
        # Add scenarios
        for scenario in feature.scenarios:
            # Scenario tags
            if scenario.tags:
                lines.append(' '.join(f'@{tag}' for tag in scenario.tags))
            
            # Scenario header
            lines.append(f"  Scenario: {scenario.name}")
            
            # Scenario steps
            for step in scenario.steps:
                step_line = f"    {step.step_type.value} {step.text}"
                lines.append(step_line)
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string for use as filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name
        """
        import re
        # Replace spaces and special characters
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '_', name)
        return name.lower().strip('_')

