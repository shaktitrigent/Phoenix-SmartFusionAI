"""Main pipeline script for SmartFusionAI."""

import argparse
import sys
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional

# External library imports (required dependencies)
try:
    from phoenix_smartlocatorai import dom_scanner, page_object_exporter  # type: ignore
except ImportError:
    dom_scanner = None
    page_object_exporter = None

try:
    from phoenix_smartcaseai import StoryBDDGenerator  # type: ignore
except ImportError:
    StoryBDDGenerator = None

from core.locator_engine import LocatorParser
from core.case_engine import BDDGenerator
from core.fusion_mapper import FusionMapper
from core.step_definitions import StepDefinitionGenerator
from core.exporters import OutputExporter
from core.utils.models import FusionConfig, LocatorType


class SmartFusionPipeline:
    """End-to-end pipeline for SmartFusionAI."""
    
    def __init__(
        self,
        output_dir: str = "output",
        framework: LocatorType = LocatorType.PLAYWRIGHT,
        strict_mode: bool = False
    ):
        """Initialize the pipeline.
        
        Args:
            output_dir: Output directory
            framework: Framework type (Playwright or Selenium)
            strict_mode: Enable strict mode (fail on unmatched locators)
        """
        self.config = FusionConfig(
            framework=framework,
            strict_mode=strict_mode,
            output_format="both"
        )
        
        self.locator_parser = LocatorParser(locator_type=framework)
        self.bdd_generator = BDDGenerator()
        self.fusion_mapper = FusionMapper(config=self.config)
        self.step_generator = StepDefinitionGenerator(framework=framework)
        self.exporter = OutputExporter(output_dir=output_dir)
    
    def run(
        self,
        user_story_path: Optional[str] = None,
        bdd_feature_path: Optional[str] = None,
        locator_file_path: Optional[str] = None,
        dom_snapshot_path: Optional[str] = None
    ):
        """Run the complete fusion pipeline.
        
        Args:
            user_story_path: Path to user story file
            bdd_feature_path: Path to existing BDD feature file
            locator_file_path: Path to locator file (page.py or locators.json)
            dom_snapshot_path: Path to DOM snapshot (optional, for future use)
        
        Returns:
            Dictionary with output paths
        """
        print("Starting SmartFusionAI Pipeline...")
        print("=" * 60)
        
        # Step 1: Parse locators
        print("\nStep 1: Parsing locators...")
        if not locator_file_path:
            raise ValueError("locator_file_path is required")
        
        locator_dict = self.locator_parser.parse(locator_file_path)
        print(f"   [OK] Found {len(locator_dict.locators)} locators")
        for name, info in locator_dict.locators.items():
            print(f"     - {name} -> {info.variable_name}")
        
        # Step 2: Generate or parse BDD feature
        print("\nStep 2: Processing BDD feature...")
        if bdd_feature_path:
            feature = self.bdd_generator.parse_feature_file(bdd_feature_path)
            print(f"   [OK] Parsed feature: {feature.feature_name}")
        elif user_story_path:
            with open(user_story_path, 'r', encoding='utf-8') as f:
                user_story = f.read()
            # Use SmartCaseAI directly through BDDGenerator
            feature = self.bdd_generator.generate_from_story(
                user_story, 
                llm_provider=getattr(self.config, 'llm_provider', 'openai')
            )
            print(f"   [OK] Generated feature from user story using SmartCaseAI")
        else:
            raise ValueError("Either bdd_feature_path or user_story_path is required")
        
        print(f"   [OK] Found {len(feature.scenarios)} scenarios")
        total_steps = sum(len(s.steps) for s in feature.scenarios)
        print(f"   [OK] Total steps: {total_steps}")
        
        # Step 3: Map BDD steps to locators
        print("\nStep 3: Mapping BDD steps to locators...")
        enhanced_feature, fusion_report = self.fusion_mapper.map_feature(
            feature,
            locator_dict
        )
        
        print(f"   [OK] Matched {fusion_report.matched_steps}/{fusion_report.total_steps} steps")
        if fusion_report.unmatched_steps > 0:
            print(f"   [WARN] Unmatched steps: {fusion_report.unmatched_steps}")
            if fusion_report.unmatched_tokens:
                print(f"   [WARN] Unmatched tokens: {', '.join(fusion_report.unmatched_tokens)}")
        
        # Step 4: Generate step definitions
        print("\nStep 4: Generating step definitions...")
        step_definitions = self.step_generator.generate(enhanced_feature)
        print(f"   [OK] Generated {self.config.framework.value} step definitions")
        
        # Step 5: Generate mapping table
        print("\nStep 5: Generating traceability mapping...")
        mapping_table = self.fusion_mapper.generate_mapping_table(
            enhanced_feature,
            locator_dict
        )
        print(f"   [OK] Generated mapping table")
        
        # Step 6: Export outputs
        print("\nStep 6: Exporting outputs...")
        
        feature_path = self.exporter.export_feature(enhanced_feature)
        print(f"   [OK] Exported feature: {feature_path}")
        
        steps_path = self.exporter.export_step_definitions(
            step_definitions,
            enhanced_feature.feature_name,
            self.config.framework
        )
        print(f"   [OK] Exported step definitions: {steps_path}")
        
        report_path = self.exporter.export_fusion_report(fusion_report)
        print(f"   [OK] Exported fusion report: {report_path}")
        
        mapping_path = self.exporter.export_mapping_table(
            mapping_table,
            enhanced_feature.feature_name
        )
        print(f"   [OK] Exported mapping table: {mapping_path}")
        
        print("\n" + "=" * 60)
        print("Pipeline completed successfully!")
        print("\nOutput files:")
        print(f"   - Enhanced Feature: {feature_path}")
        print(f"   - Step Definitions: {steps_path}")
        print(f"   - Fusion Report: {report_path}")
        print(f"   - Mapping Table: {mapping_path}")
        
        return {
            "feature": str(feature_path),
            "step_definitions": str(steps_path),
            "fusion_report": str(report_path),
            "mapping_table": str(mapping_path)
        }
    
    def run_auto_mode(
        self,
        url: str,
        user_story: Optional[str] = None,
        user_story_file: Optional[str] = None,
        dom_snapshot_path: Optional[str] = None,
        context_files: Optional[list] = None,
        llm_provider: str = "openai"
    ):
        """Run in auto mode - generate everything automatically.
        
        Args:
            url: URL to automate
            user_story: User story as text string
            user_story_file: Path to user story file
            dom_snapshot_path: Optional DOM snapshot file path
            context_files: List of additional context files (PDF, images, etc.)
            llm_provider: LLM provider for SmartCaseAI (openai, gemini, claude)
            
        Returns:
            Dictionary with all output paths including generated locators
        """
        print("Starting SmartFusionAI Auto Mode...")
        print("=" * 60)
        print("This mode will automatically generate:")
        print("  1. Locators (locators.json + page.py) from URL")
        print("  2. BDD Feature file from user story")
        print("  3. Enhanced feature with locator mapping")
        print("  4. PyTest automation test code")
        print("=" * 60)
        
        # Step 1: Generate locators from URL using SmartLocatorAI
        print("\n[Step 1/6] Generating locators from URL...")
        locator_file_path = None
        page_py_path = None
        
        # Use SmartLocatorAI modular components: dom_scanner and page_object_exporter
        if dom_scanner is None or page_object_exporter is None:
            raise ImportError(
                "phoenix-smartlocatorai package not found. Please install it: "
                "pip install phoenix-smartlocatorai"
            )
        
        # Step 1: Scan DOM to get locators
        input_source = dom_snapshot_path if (dom_snapshot_path and Path(dom_snapshot_path).exists()) else url
        if dom_snapshot_path and Path(dom_snapshot_path).exists():
            print(f"   [INFO] Using DOM snapshot: {dom_snapshot_path}")
            # Read HTML file
            with open(dom_snapshot_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            locators = dom_scanner.scan_dom(html_content, js_render=False)
        else:
            print(f"   [INFO] Fetching DOM from URL: {url}")
            # Scan from URL (dom_scanner handles URL fetching)
            locators = dom_scanner.scan_dom(url, js_render=False)
        
        if not locators:
            raise ValueError("No locators generated from the provided URL/HTML")
        
        print(f"   [OK] Scanned {len(locators)} elements from DOM")
        
        # Step 2: Save locators to JSON
        target_locators_dir = Path(self.exporter.output_dir) / "generated_locators"
        target_locators_dir.mkdir(parents=True, exist_ok=True)
        
        locators_json_path = target_locators_dir / "locators.json"
        with open(locators_json_path, 'w', encoding='utf-8') as f:
            json.dump({"locators": locators}, f, indent=2, ensure_ascii=False)
        
        locator_file_path = str(locators_json_path)
        print(f"   [OK] Generated locators.json: {locator_file_path}")
        
        # Step 3: Generate Page Object Model
        framework_str = "playwright" if self.config.framework == LocatorType.PLAYWRIGHT else "selenium"
        class_name = "GeneratedPage"
        
        if framework_str == "playwright":
            page_object_code = page_object_exporter.generate_playwright_pom(
                locators=locators,
                class_name=class_name
            )
        else:
            page_object_code = page_object_exporter.generate_selenium_pom(
                locators=locators,
                class_name=class_name
            )
        
        # Save Page Object to file
        page_py_path = target_locators_dir / "page.py"
        with open(page_py_path, 'w', encoding='utf-8') as f:
            f.write(page_object_code)
        
        page_py_path = str(page_py_path)
        print(f"   [OK] Generated page.py: {page_py_path}")
        
        # Step 2: Process user story and context files
        print("\n[Step 2/6] Processing user story and context files...")
        user_story_text = user_story
        
        if user_story_file:
            if Path(user_story_file).exists():
                with open(user_story_file, 'r', encoding='utf-8') as f:
                    user_story_text = f.read()
                print(f"   [OK] Loaded user story from: {user_story_file}")
            else:
                print(f"   [WARN] User story file not found: {user_story_file}")
        
        if not user_story_text:
            raise ValueError("User story is required (provide --user-story-text or --user-story-file)")
        
        # Step 3: Generate BDD feature from user story using SmartCaseAI
        print("\n[Step 3/6] Generating BDD feature from user story...")
        if StoryBDDGenerator is None:
            raise ImportError(
                "phoenix-smartcaseai package not found. Please install it: "
                "pip install phoenix-smartcaseai"
            )
        
        bdd_generator = StoryBDDGenerator(llm_provider=llm_provider)
        
        if context_files:
            print(f"   [INFO] Passing {len(context_files)} context file(s) to SmartCaseAI...")
        
        # SmartCaseAI handles everything - file processing, LLM calls, BDD generation
        feature_content = bdd_generator.generate_test_cases(
            user_story=user_story_text,
            output_format="gherkin",
            additional_files=context_files  # SmartCaseAI processes these automatically
        )
        
        # Save generated feature file
        feature_file_path = Path(self.exporter.output_dir) / "generated_bdd" / "generated_feature.feature"
        feature_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(feature_file_path, 'w', encoding='utf-8') as f:
            f.write(feature_content)
        print(f"   [OK] Generated BDD feature: {feature_file_path}")
        
        # Parse the generated feature
        feature = self.bdd_generator.parse_feature_content(feature_content)
        
        print(f"   [OK] Generated {len(feature.scenarios)} scenarios")
        
        # Step 4: Parse generated locators
        print("\n[Step 4/6] Parsing generated locators...")
        locator_dict = self.locator_parser.parse(locator_file_path)
        print(f"   [OK] Found {len(locator_dict.locators)} locators")
        
        # Step 5: Map BDD steps to locators
        print("\n[Step 5/6] Mapping BDD steps to locators...")
        enhanced_feature, fusion_report = self.fusion_mapper.map_feature(
            feature,
            locator_dict
        )
        print(f"   [OK] Matched {fusion_report.matched_steps}/{fusion_report.total_steps} steps")
        
        # Step 6: Generate step definitions and export
        print("\n[Step 6/6] Generating step definitions and exporting...")
        step_definitions = self.step_generator.generate(enhanced_feature)
        mapping_table = self.fusion_mapper.generate_mapping_table(enhanced_feature, locator_dict)
        
        # Export all outputs
        feature_path = self.exporter.export_feature(enhanced_feature)
        steps_path = self.exporter.export_step_definitions(
            step_definitions,
            enhanced_feature.feature_name,
            self.config.framework
        )
        report_path = self.exporter.export_fusion_report(fusion_report)
        mapping_path = self.exporter.export_mapping_table(
            mapping_table,
            enhanced_feature.feature_name
        )
        
        print("\n" + "=" * 60)
        print("Auto Mode completed successfully!")
        print("\nGenerated Files:")
        print(f"   - Locators JSON: {locator_file_path}")
        if page_py_path:
            print(f"   - Page Object: {page_py_path}")
        print(f"   - BDD Feature: {feature_path}")
        print(f"   - Step Definitions: {steps_path}")
        print(f"   - Fusion Report: {report_path}")
        print(f"   - Mapping Table: {mapping_path}")
        print("=" * 60)
        
        return {
            "locators_json": str(locator_file_path),
            "page_py": str(page_py_path) if page_py_path else None,
            "feature": str(feature_path),
            "step_definitions": str(steps_path),
            "fusion_report": str(report_path),
            "mapping_table": str(mapping_path)
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SmartFusionAI - Unified Engine for BDD + Locators"
    )
    
    parser.add_argument(
        "--user-story",
        type=str,
        help="Path to user story file (.txt)"
    )
    
    parser.add_argument(
        "--bdd-feature",
        type=str,
        help="Path to BDD feature file (.feature)"
    )
    
    parser.add_argument(
        "--locator-file",
        type=str,
        required=True,
        help="Path to locator file (page.py or locators.json)"
    )
    
    parser.add_argument(
        "--dom-snapshot",
        type=str,
        help="Path to DOM snapshot file (.html)"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="URL to fetch DOM snapshot from (requires SmartLocatorAI)"
    )
    
    parser.add_argument(
        "--user-stories",
        type=str,
        nargs="+",
        help="Multiple user story files to process (batch mode)"
    )
    
    parser.add_argument(
        "--bdd-features",
        type=str,
        nargs="+",
        help="Multiple BDD feature files to process (batch mode)"
    )
    
    parser.add_argument(
        "--case-study",
        type=str,
        help="Path to case study/requirements document (.txt, .md, .pdf)"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Enable batch processing mode for multiple files"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory (default: output)"
    )
    
    parser.add_argument(
        "--framework",
        type=str,
        choices=["playwright", "selenium"],
        default="playwright",
        help="Test framework (default: playwright)"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (fail on unmatched locators)"
    )
    
    parser.add_argument(
        "--generate-locators",
        action="store_true",
        help="Generate locators from URL or DOM snapshot using SmartLocatorAI"
    )
    
    # Auto mode arguments
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Enable auto mode: automatically generate everything from URL + user story"
    )
    
    parser.add_argument(
        "--user-story-text",
        type=str,
        help="User story as text string (for auto mode)"
    )
    
    parser.add_argument(
        "--context-files",
        type=str,
        nargs="+",
        help="Additional context files (PDF, images, documents, PPT, etc.) for auto mode"
    )
    
    parser.add_argument(
        "--llm-provider",
        type=str,
        choices=["openai", "gemini", "claude"],
        default="openai",
        help="LLM provider for SmartCaseAI (default: openai)"
    )
    
    args = parser.parse_args()
    
    # Handle auto mode first
    if args.auto:
        if not args.url:
            parser.error("--url is required for auto mode")
        if not args.user_story_text and not args.user_story:
            parser.error("User story is required for auto mode (use --user-story-text or --user-story)")
        
        framework = LocatorType.PLAYWRIGHT if args.framework == "playwright" else LocatorType.SELENIUM
        
        pipeline = SmartFusionPipeline(
            output_dir=args.output_dir,
            framework=framework,
            strict_mode=args.strict
        )
        
        try:
            pipeline.run_auto_mode(
                url=args.url,
                user_story=args.user_story_text,
                user_story_file=args.user_story,
                dom_snapshot_path=args.dom_snapshot,
                context_files=args.context_files,
                llm_provider=args.llm_provider
            )
        except Exception as e:
            print(f"\n[ERROR] {e}", file=sys.stderr)
            sys.exit(1)
        
        return
    
    # Validate inputs for normal mode
    user_stories = args.user_stories or ([args.user_story] if args.user_story else [])
    bdd_features = args.bdd_features or ([args.bdd_feature] if args.bdd_feature else [])
    
    if not user_stories and not bdd_features:
        parser.error("Either --user-story/--user-stories or --bdd-feature/--bdd-features is required")
    
    # Validate file existence
    for story_path in user_stories:
        if story_path and not Path(story_path).exists():
            parser.error(f"User story file not found: {story_path}")
    
    for feature_path in bdd_features:
        if feature_path and not Path(feature_path).exists():
            parser.error(f"BDD feature file not found: {feature_path}")
    
    # Handle URL-based locator generation
    locator_file_path = args.locator_file
    if args.generate_locators and args.url:
        print("Generating locators from URL using SmartLocatorAI...")
        # Use SmartLocatorAI modular components
        if dom_scanner is None or page_object_exporter is None:
            raise ImportError(
                "phoenix-smartlocatorai package not found. Please install it: "
                "pip install phoenix-smartlocatorai"
            )
        
        # Scan DOM from URL
        locators = dom_scanner.scan_dom(args.url, js_render=False)
        
        if not locators:
            raise ValueError("No locators generated from the provided URL")
        
        print(f"   [OK] Scanned {len(locators)} elements from DOM")
        
        # Save to temporary JSON file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
        json.dump({"locators": locators}, temp_file, indent=2, ensure_ascii=False)
        temp_file.close()
        locator_file_path = temp_file.name
        print(f"   [OK] Generated locators saved to: {locator_file_path}")
    
    # For normal mode, locator file is required unless generating from URL
    if not args.generate_locators and (not locator_file_path or not Path(locator_file_path).exists()):
        parser.error(f"Locator file not found: {locator_file_path}")
    
    # Run pipeline
    framework = LocatorType.PLAYWRIGHT if args.framework == "playwright" else LocatorType.SELENIUM
    
    pipeline = SmartFusionPipeline(
        output_dir=args.output_dir,
        framework=framework,
        strict_mode=args.strict
    )
    
    # Batch processing mode
    if args.batch or len(user_stories) > 1 or len(bdd_features) > 1:
        print(f"\nBatch Processing Mode: Processing {len(user_stories) + len(bdd_features)} files...")
        results = []
        
        # Process user stories
        for i, story_path in enumerate(user_stories, 1):
            if not story_path:
                continue
            print(f"\n{'='*60}")
            print(f"Processing User Story {i}/{len(user_stories)}: {story_path}")
            print('='*60)
            try:
                result = pipeline.run(
                    user_story_path=story_path,
                    locator_file_path=locator_file_path,
                    dom_snapshot_path=args.dom_snapshot
                )
                results.append(result)
            except Exception as e:
                print(f"\n[ERROR] Failed to process {story_path}: {e}", file=sys.stderr)
                if args.strict:
                    sys.exit(1)
        
        # Process BDD features
        for i, feature_path in enumerate(bdd_features, 1):
            if not feature_path:
                continue
            print(f"\n{'='*60}")
            print(f"Processing BDD Feature {i}/{len(bdd_features)}: {feature_path}")
            print('='*60)
            try:
                result = pipeline.run(
                    bdd_feature_path=feature_path,
                    locator_file_path=locator_file_path,
                    dom_snapshot_path=args.dom_snapshot
                )
                results.append(result)
            except Exception as e:
                print(f"\n[ERROR] Failed to process {feature_path}: {e}", file=sys.stderr)
                if args.strict:
                    sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"Batch Processing Complete: {len(results)} files processed successfully")
        print('='*60)
    else:
        # Single file processing
        try:
            pipeline.run(
                user_story_path=args.user_story,
                bdd_feature_path=args.bdd_feature,
                locator_file_path=locator_file_path,
                dom_snapshot_path=args.dom_snapshot
            )
        except Exception as e:
            print(f"\n[ERROR] {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

