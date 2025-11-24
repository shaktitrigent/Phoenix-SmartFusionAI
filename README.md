# Phoenix-SmartFusionAI

**SmartFusionAI – A Unified Engine for BDD + Locators**

SmartFusionAI merges [SmartCaseAI](https://github.com/shaktitrigent/Phoenix-SmartCaseAI) (BDD test generation) and [SmartLocatorAI](https://github.com/shaktitrigent/Phoenix-SmartLocatorAI) (web locator generation) into a unified system that automatically generates executable test code from user stories.

## 🎯 Overview

SmartFusionAI takes:
- **User Story** (plain text) - Single or multiple files
- **DOM Snapshot** or **URL** - For automatic locator generation
- **Generated Locators** (page.py + locators.json)
- **Generated BDD** (.feature file) - Single or multiple files
- **Case Study/Requirements** (optional) - Additional context

And outputs:
- **Enhanced BDD .feature file** with embedded locator references
- **Auto-generated Python Step Definition files** (Playwright/Selenium)
- **Traceability Report** showing story → BDD step → locator mapping

### ✨ Key Features

- ✅ **Auto Mode**: Generate everything automatically from URL + user story (NEW!)
- ✅ **URL-Based Automation**: Generate locators directly from URLs
- ✅ **Batch Processing**: Process multiple user stories or BDD features at once
- ✅ **Context File Support**: Include PDFs, images, documents, PPTs for enhanced context
- ✅ **Multi-Framework**: Support for Playwright (primary) and Selenium (secondary)
- ✅ **Intelligent Mapping**: Automatic token extraction and locator binding
- ✅ **Traceability**: Complete mapping from user story to executable code

## 🏗️ Architecture

```
┌─────────────────┐
│  User Story     │
│  DOM Snapshot   │
│  Locators       │
│  BDD Feature    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      SmartFusionAI Pipeline         │
├─────────────────────────────────────┤
│ 1. Locator Parser                  │
│ 2. BDD Generator                    │
│ 3. Fusion Mapper (Core Engine)      │
│ 4. Step Definition Generator        │
│ 5. Output Exporter                  │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  Enhanced .feature                  │
│  Step Definitions (.py)             │
│  Fusion Report (.json)              │
│  Mapping Table (.json)              │
└─────────────────────────────────────┘
```

## 📁 Project Structure

```
Phoenix-SmartFusionAI/
├── core/
│   ├── case_engine/          # BDD test case generation
│   │   └── generator.py
│   ├── locator_engine/       # Locator parsing
│   │   └── parser.py
│   ├── fusion_mapper/        # Core fusion engine
│   │   └── mapper.py
│   ├── step_definitions/     # Step definition generation
│   │   └── generator.py
│   ├── exporters/            # Output file generation
│   │   └── exporter.py
│   └── utils/                # Models and utilities
│       └── models.py
├── data/
│   ├── user_stories/         # Input user stories
│   ├── dom_snapshots/        # DOM snapshots
│   ├── generated_locators/   # Generated locator files
│   └── generated_bdd/         # Generated BDD files
├── output/
│   ├── merged_feature_files/ # Enhanced .feature files
│   ├── python_tests/         # Generated step definitions
│   └── fusion_reports/       # Mapping reports
├── examples/                 # Example files
├── tests/                    # Unit tests
├── main.py                   # Main pipeline script
├── requirements.txt
└── setup.py
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shaktitrigent/Phoenix-SmartFusionAI.git
cd Phoenix-SmartFusionAI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install required external libraries (from local wheels or PyPI)
pip install phoenix-smartlocatorai phoenix-smartcaseai

# Install in development mode (optional)
pip install -e .
```

### Basic Usage

```bash
# Run with BDD feature file and locators
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_locators.json \
  --framework playwright \
  --output-dir output
```

### Command Line Options

```bash
python main.py --help

Auto Mode Options (--auto):
  --auto                      Enable auto mode: generate everything automatically
  --url URL                   URL to automate (REQUIRED for auto mode)
  --user-story-text TEXT      User story as text string
  --user-story PATH           Path to user story file (.txt)
  --dom-snapshot PATH         Optional DOM snapshot file (.html)
  --context-files PATH ...    Additional context files (PDF, images, documents, PPT, etc.)
  --llm-provider {openai,gemini,claude}  LLM provider for SmartCaseAI (default: openai)

Manual Mode Options:
  --user-story PATH           Path to user story file (.txt)
  --user-stories PATH ...     Multiple user story files (batch mode)
  --bdd-feature PATH         Path to BDD feature file (.feature)
  --bdd-features PATH ...     Multiple BDD feature files (batch mode)
  --locator-file PATH         Path to locator file (page.py or locators.json) [REQUIRED for manual mode]
  --dom-snapshot PATH         Path to DOM snapshot file (.html)
  --url URL                   URL to fetch DOM snapshot from
  --case-study PATH           Path to case study/requirements document
  --generate-locators          Generate locators from URL or DOM snapshot using SmartLocatorAI
  --batch                     Enable batch processing mode (optional - auto-detected)

Common Options:
  --output-dir PATH           Output directory (default: output)
  --framework {playwright,selenium}  Test framework (default: playwright)
  --strict                    Enable strict mode (fail on unmatched locators)
```

## 📖 Usage Examples

### Example 1: Using Existing BDD Feature

```bash
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_locators.json \
  --framework playwright
```

**Input BDD Feature:**
```gherkin
Feature: User Login

  Scenario: Valid Login
    Given I am on the login page
    When I enter "user_name"
    And I enter "password"
    And I click on "submit"
    Then I should see "dashboard"
```

**Output Enhanced Feature:**
```gherkin
Feature: User Login

  Scenario: Valid Login
    Given I am on the login page
    When I enter text into ${self.user_name_input}
    And I enter text into ${self.password_input}
    And I click on ${self.submit_button}
    Then I should see ${self.dashboard_title}
```

### Example 2: Using User Story

```bash
python main.py \
  --user-story examples/example_user_story.txt \
  --locator-file examples/example_locators.json \
  --framework playwright
```

### Example 3: Using Page Object (page.py)

```bash
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_page.py \
  --framework playwright
```

### Example 4: URL-Based Automation (Generate Locators from URL)

```bash
# Generate locators from URL and create tests
python main.py \
  --user-story examples/orangehrm_user_story.txt \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --generate-locators \
  --framework playwright
```

### Example 5: Batch Processing - Multiple User Stories

```bash
# Process multiple user stories at once
# Note: --batch is optional - automatically detected when multiple files provided
python main.py \
  --user-stories \
    examples/user_story_1.txt \
    examples/user_story_2.txt \
    examples/user_story_3.txt \
  --locator-file examples/locators.json \
  --framework playwright

# Or explicitly with --batch flag (optional)
python main.py \
  --user-stories \
    examples/user_story_1.txt \
    examples/user_story_2.txt \
    examples/user_story_3.txt \
  --locator-file examples/locators.json \
  --batch \
  --framework playwright
```

### Example 6: Batch Processing - Multiple BDD Features

```bash
# Process multiple BDD features at once
# Note: --batch is optional - automatically detected when multiple files provided
python main.py \
  --bdd-features \
    examples/login.feature \
    examples/registration.feature \
    examples/dashboard.feature \
  --locator-file examples/locators.json \
  --framework playwright

# Or explicitly with --batch flag (optional)
python main.py \
  --bdd-features \
    examples/login.feature \
    examples/registration.feature \
    examples/dashboard.feature \
  --locator-file examples/locators.json \
  --batch \
  --framework playwright
```

### Example 7: With Case Study/Requirements Document

```bash
# Include case study for additional context
python main.py \
  --user-story examples/user_story.txt \
  --case-study examples/requirements.pdf \
  --locator-file examples/locators.json \
  --framework playwright
```

### Example 8: URL + DOM Snapshot

```bash
# Use URL to generate locators and DOM snapshot for reference
python main.py \
  --bdd-feature examples/login.feature \
  --url "https://example.com/login" \
  --dom-snapshot data/dom_snapshots/login_page.html \
  --generate-locators \
  --framework playwright
```

### Example 9: Selenium Framework

```bash
# Generate Selenium step definitions instead of Playwright
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_locators.json \
  --framework selenium
```

### Example 10: Strict Mode

```bash
# Fail if any locators are unmatched
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_locators.json \
  --strict \
  --framework playwright
```

### Example 11: Custom Output Directory

```bash
# Specify custom output directory
python main.py \
  --bdd-feature examples/example_bdd.feature \
  --locator-file examples/example_locators.json \
  --output-dir my_tests \
  --framework playwright
```

### Example 12: Complete Workflow - URL to Executable Tests

```bash
# End-to-end: URL → Locators → BDD → Executable Tests
python main.py \
  --user-story examples/orangehrm_story.txt \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --generate-locators \
  --case-study examples/orangehrm_requirements.txt \
  --output-dir orangehrm_tests \
  --framework playwright
```

## 🌐 URL-Based Automation

SmartFusionAI supports URL-based automation where you can provide a URL and automatically generate locators and tests using [Phoenix-SmartLocatorAI](https://github.com/shaktitrigent/Phoenix-SmartLocatorAI).

### Prerequisites
- **SmartLocatorAI** must be installed: `pip install phoenix-smartlocatorai`
- **SmartCaseAI** must be installed: `pip install phoenix-smartcaseai` (for auto mode)
- API keys for LLM providers (if using SmartCaseAI for BDD generation)

### SmartLocatorAI Integration

SmartFusionAI uses SmartLocatorAI's modular components directly:
- **`dom_scanner`**: Scans DOM from URL or HTML file, returns list of locator dictionaries
- **`page_object_exporter`**: Generates Page Object Model code from locator dictionaries
- Supports framework selection (Playwright/Selenium)
- No hardcoded paths - uses installed package modules

**SmartLocatorAI Integration Flow:**
1. `dom_scanner.scan_dom(url_or_html)` → Returns list of locator dictionaries
2. Save locators to `locators.json` with metadata
3. `page_object_exporter.generate_playwright_pom()` or `generate_selenium_pom()` → Generates Page Object code
4. Save `page.py` to output directory

**Output Format:**
- `locators.json` - JSON with `{"locators": [...]}` array containing all element dictionaries
- `page.py` - Standardized Page Object Model for selected framework

### URL Automation Workflow

```bash
# Auto mode: Generate everything from URL + user story
python main.py \
  --auto \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --user-story examples/orangehrm_story.txt \
  --framework playwright
```

**Manual mode with URL:**
```bash
python main.py \
  --user-story examples/orangehrm_story.txt \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --generate-locators \
  --framework playwright
```

This command will:
1. Scan DOM from the provided URL using `dom_scanner.scan_dom()`
2. Generate locator dictionaries for all interactable elements
3. Save `locators.json` and generate `page.py` to `output/generated_locators/`
4. Generate BDD from user story using SmartCaseAI
5. Map BDD steps to generated locators
6. Create executable PyTest test code

## 📦 Batch Processing

SmartFusionAI supports processing multiple user stories or BDD features in a single run.

### When is `--batch` Required?

**Answer: `--batch` is NOT required!** It's completely optional.

The system **automatically detects** batch mode when you provide multiple files:
- `--user-stories file1.txt file2.txt` (2+ files) → **Auto batch mode** ✅
- `--bdd-features file1.feature file2.feature` (2+ files) → **Auto batch mode** ✅

You can still use `--batch` explicitly for clarity, but it's not necessary.

### Batch Processing User Stories

```bash
# Without --batch (auto-detected)
python main.py \
  --user-stories \
    data/stories/login_story.txt \
    data/stories/registration_story.txt \
    data/stories/dashboard_story.txt \
  --locator-file examples/locators.json \
  --framework playwright

# With --batch (explicit, but optional)
python main.py \
  --user-stories \
    data/stories/login_story.txt \
    data/stories/registration_story.txt \
    data/stories/dashboard_story.txt \
  --locator-file examples/locators.json \
  --batch \
  --framework playwright
```

### Batch Processing BDD Features

```bash
# Without --batch (auto-detected)
python main.py \
  --bdd-features \
    examples/login.feature \
    examples/registration.feature \
    examples/dashboard.feature \
  --locator-file examples/locators.json \
  --framework playwright

# With --batch (explicit, but optional)
python main.py \
  --bdd-features \
    examples/login.feature \
    examples/registration.feature \
    examples/dashboard.feature \
  --locator-file examples/locators.json \
  --batch \
  --framework playwright
```

### Batch Processing Benefits

- **Efficiency**: Process multiple files in one command
- **Consistency**: Same locator file used for all tests
- **Organization**: Output files organized by feature/story name
- **Progress Tracking**: See progress for each file being processed
- **Auto-Detection**: No need to remember `--batch` flag - just provide multiple files!

## 🔧 Core Components

### 1. Locator Parser

Parses locator files and extracts:
- Element variable names (`self.user_name_input`)
- Locator expressions (`page.locator('#username')`)
- Normalized element names (`user_name`)

**Supported Formats:**
- `page.py` - Python page object files
- `locators.json` - JSON locator definitions

### 2. BDD Generator

Generates or parses BDD test cases:
- Parses existing `.feature` files
- Generates BDD from user stories (integrates with SmartCaseAI)
- Extracts tokens from step text
- **File Processing**: SmartCaseAI automatically processes context files (PDFs, images, documents, PPTs) via `additional_files` parameter - no manual processing needed

### 3. Fusion Mapper (Core Engine)

Maps BDD steps to locator variables:
- **Exact Matching**: Direct token → locator mapping
- **Partial Matching**: Fuzzy matching for similar names
- **Token Extraction**: Identifies UI elements from step text
- **Step Rewriting**: Embeds locator variables in step text

**Mapping Rules:**
- `enter "field"` → `${self.field_input}`
- `click on "button"` → `${self.button_locator}`
- `select "option"` → `${self.option_selector}`

### 4. Step Definition Generator

Generates Python step definitions for:
- **Playwright**: Uses `page.locator()` and Playwright API
- **Selenium**: Uses `find_element()` and Selenium API

### 5. Output Exporter

Exports:
- Enhanced `.feature` files
- Python step definition files
- Fusion mapping reports (JSON)
- Traceability mapping tables (JSON)

## 📊 Output Files

### Enhanced Feature File

```gherkin
Feature: User Login

  Scenario: Valid Login
    Given I am on the login page
    When I enter text into ${self.user_name_input}
    And I enter text into ${self.password_input}
    And I click on ${self.submit_button}
    Then I should see ${self.dashboard_title}
```

### Step Definitions (Playwright)

```python
"""Auto-generated step definitions for Playwright."""

from behave import given, when, then, step
from playwright.sync_api import Page, expect

@when('^I enter text into (?P<locator>\S+)$')
def step_when_enter_text(context, locator=None, value=None, **kwargs):
    """Enter text into a field."""
    if locator and hasattr(context, "page"):
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1]
            element = getattr(context.page, locator_var.split(".")[-1], None)
            if element and value:
                element.fill(value)
```

### Fusion Report

```json
{
  "feature_name": "User Login",
  "total_steps": 5,
  "matched_steps": 4,
  "unmatched_steps": 1,
  "mappings": [
    {
      "step": {
        "step_type": "When",
        "text": "I enter \"user_name\"",
        "tokens": ["user_name"]
      },
      "matched": true,
      "locator_variable": "self.user_name_input",
      "match_type": "exact"
    }
  ],
  "unmatched_tokens": ["unknown_element"],
  "warnings": []
}
```

## 🔍 Intelligent Mapping

### Mapping Strategy

1. **Exact Match**: Token exactly matches normalized locator name
2. **Partial Match**: Token partially matches locator name (if enabled)
3. **No Match**: Token not found → warning generated

### Token Extraction Patterns

- **Input Steps**: `enter "field"`, `fill "field"`, `type in "field"`
- **Click Steps**: `click on "button"`, `press "button"`
- **Select Steps**: `select "option"`, `choose "option"`
- **Assert Steps**: `see "text"`, `verify "element"`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test file
pytest tests/test_fusion_mapper.py
```

## 🔌 Integration

### With SmartCaseAI

```python
from phoenix_smartcaseai import StoryBDDGenerator
from core.fusion_mapper import FusionMapper
from core.locator_engine import LocatorParser

# Generate BDD from user story
bdd_generator = StoryBDDGenerator(llm_provider="openai")
feature = bdd_generator.generate_test_cases(
    user_story="As a user, I want to log in.",
    output_format="bdd"
)

# Parse locators
locator_parser = LocatorParser()
locator_dict = locator_parser.parse("locators.json")

# Map BDD to locators
fusion_mapper = FusionMapper()
enhanced_feature, report = fusion_mapper.map_feature(feature, locator_dict)
```

### With SmartLocatorAI

SmartFusionAI integrates with [Phoenix-SmartLocatorAI](https://github.com/shaktitrigent/Phoenix-SmartLocatorAI) to automatically generate locators using modular components.

**Programmatic Usage:**
```python
from phoenix_smartlocatorai import dom_scanner, page_object_exporter
import json

# Step 1: Scan DOM to get locators
locators = dom_scanner.scan_dom("https://example.com", js_render=False)

# Step 2: Save locators to JSON
with open("locators.json", 'w') as f:
    json.dump({"locators": locators}, f, indent=2)

# Step 3: Generate Page Object Model
page_object_code = page_object_exporter.generate_playwright_pom(
    locators=locators,
    class_name="ProductPage"
)

# Save Page Object to file
with open("page.py", 'w') as f:
    f.write(page_object_code)
```

**Auto Mode Integration:**
- SmartFusionAI automatically uses `dom_scanner` and `page_object_exporter` when `--auto` mode is used
- Locators are generated and saved to `output/generated_locators/`
- Both `locators.json` and `page.py` are generated automatically
- No hardcoded paths - uses installed package modules directly

## 🚀 Advanced Command Line Usage

### Complete Command Reference

#### Basic Syntax
```bash
python main.py [OPTIONS]
```

#### Required Arguments
- `--locator-file PATH` - Path to locator file (page.py or locators.json)

#### Input Options (at least one required)
- `--user-story PATH` - Single user story file
- `--user-stories PATH ...` - Multiple user story files (batch mode)
- `--bdd-feature PATH` - Single BDD feature file
- `--bdd-features PATH ...` - Multiple BDD feature files (batch mode)

#### Optional Arguments
- `--url URL` - URL to fetch DOM snapshot from
- `--dom-snapshot PATH` - Path to DOM snapshot file (.html)
- `--case-study PATH` - Path to case study/requirements document
- `--generate-locators` - Generate locators from URL/DOM using SmartLocatorAI
- `--batch` - Enable batch processing mode
- `--output-dir PATH` - Output directory (default: output)
- `--framework {playwright,selenium}` - Test framework (default: playwright)
- `--strict` - Enable strict mode (fail on unmatched locators)

### Command Line Examples by Use Case

#### 1. Single User Story Processing
```bash
python main.py \
  --user-story data/user_stories/login_story.txt \
  --locator-file examples/locators.json \
  --framework playwright
```

#### 2. Single BDD Feature Processing
```bash
python main.py \
  --bdd-feature examples/login.feature \
  --locator-file examples/locators.json \
  --framework playwright
```

#### 3. URL-Based Automation (Auto-Generate Locators)
```bash
python main.py \
  --user-story examples/orangehrm_story.txt \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --generate-locators \
  --framework playwright
```

#### 4. Batch Processing - Multiple User Stories
```bash
python main.py \
  --user-stories \
    data/user_stories/story1.txt \
    data/user_stories/story2.txt \
    data/user_stories/story3.txt \
  --locator-file examples/locators.json \
  --batch \
  --output-dir batch_output \
  --framework playwright
```

#### 5. Batch Processing - Multiple BDD Features
```bash
python main.py \
  --bdd-features \
    examples/login.feature \
    examples/registration.feature \
    examples/dashboard.feature \
  --locator-file examples/locators.json \
  --batch \
  --framework playwright
```

#### 6. With Case Study/Requirements
```bash
python main.py \
  --user-story examples/user_story.txt \
  --case-study examples/requirements.pdf \
  --locator-file examples/locators.json \
  --framework playwright
```

#### 7. URL + DOM Snapshot
```bash
python main.py \
  --bdd-feature examples/login.feature \
  --url "https://example.com/login" \
  --dom-snapshot data/dom_snapshots/login.html \
  --generate-locators \
  --framework playwright
```

#### 8. Selenium Framework
```bash
python main.py \
  --bdd-feature examples/login.feature \
  --locator-file examples/locators.json \
  --framework selenium
```

#### 9. Strict Mode (Fail on Unmatched Locators)
```bash
python main.py \
  --bdd-feature examples/login.feature \
  --locator-file examples/locators.json \
  --strict \
  --framework playwright
```

#### 10. Custom Output Directory
```bash
python main.py \
  --bdd-feature examples/login.feature \
  --locator-file examples/locators.json \
  --output-dir my_custom_tests \
  --framework playwright
```

#### 11. Complete End-to-End Workflow
```bash
# URL → Generate Locators → User Story → BDD → Executable Tests
python main.py \
  --user-story examples/orangehrm_story.txt \
  --url "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login" \
  --generate-locators \
  --case-study examples/orangehrm_requirements.txt \
  --output-dir orangehrm_tests \
  --framework playwright
```

#### 12. Mixed Batch Processing
```bash
# Process both user stories and BDD features together
# Note: --batch is optional - automatically detected when multiple files provided
python main.py \
  --user-stories data/story1.txt data/story2.txt \
  --bdd-features examples/feature1.feature examples/feature2.feature \
  --locator-file examples/locators.json \
  --framework playwright
```

### Command Line Quick Reference Table

| Use Case | Command |
|----------|---------|
| **🎯 Auto Mode (Simplest)** | `python main.py --auto --url URL --user-story-text "story text"` |
| **Auto Mode with File** | `python main.py --auto --url URL --user-story FILE.txt` |
| **Auto Mode with Context** | `python main.py --auto --url URL --user-story FILE.txt --context-files FILE.pdf IMG.png` |
| **Single BDD Feature** | `python main.py --bdd-feature FILE.feature --locator-file FILE.json` |
| **Single User Story** | `python main.py --user-story FILE.txt --locator-file FILE.json` |
| **URL Automation** | `python main.py --user-story FILE.txt --url URL --generate-locators` |
| **Batch User Stories** | `python main.py --user-stories FILE1.txt FILE2.txt --locator-file FILE.json` (--batch optional) |
| **Batch BDD Features** | `python main.py --bdd-features FILE1.feature FILE2.feature --locator-file FILE.json` (--batch optional) |
| **With Case Study** | `python main.py --user-story FILE.txt --case-study FILE.pdf --locator-file FILE.json` |
| **Selenium Framework** | `python main.py --bdd-feature FILE.feature --locator-file FILE.json --framework selenium` |
| **Strict Mode** | `python main.py --bdd-feature FILE.feature --locator-file FILE.json --strict` |
| **Custom Output** | `python main.py --bdd-feature FILE.feature --locator-file FILE.json --output-dir DIR` |

### Batch Processing Notes

**When is `--batch` required?**
- **NOT REQUIRED** - The `--batch` flag is **optional**
- Batch mode is **automatically detected** when you provide multiple files:
  - `--user-stories file1.txt file2.txt` (2+ files) → Auto batch mode
  - `--bdd-features file1.feature file2.feature` (2+ files) → Auto batch mode
- You can still use `--batch` explicitly for clarity, but it's not necessary

**When to use `--batch` explicitly:**
- When you want to make it clear in your command that you're doing batch processing
- When you might have edge cases where auto-detection might not work as expected
- For documentation/clarity purposes in scripts

**How batch processing works:**
- Each file is processed independently
- Output files are organized by feature/story name
- If `--strict` is enabled, any failure stops the batch
- Progress is shown for each file in the batch
- Same locator file is used for all files in the batch

## 📝 Configuration

### FusionConfig

```python
from core.utils.models import FusionConfig, LocatorType

config = FusionConfig(
    framework=LocatorType.PLAYWRIGHT,
    enable_partial_matching=True,
    strict_mode=False,
    output_format="both"
)
```

## 🎨 Example Workflow

1. **Generate Locators** (using SmartLocatorAI):
   ```bash
   # Produces: page.py and locators.json
   ```

2. **Generate BDD** (using SmartCaseAI):
   ```bash
   # Produces: login.feature
   ```

3. **Run Fusion**:
   ```bash
   python main.py \
     --bdd-feature login.feature \
     --locator-file page.py \
     --framework playwright
   ```

4. **Output**:
   - `output/merged_feature_files/login.feature` (enhanced)
   - `output/python_tests/test_login_steps.py` (step definitions)
   - `output/fusion_reports/login_fusion_report.json` (mapping report)
   - `output/fusion_reports/login_mapping_table.json` (traceability)

## 🚧 Roadmap

- [x] Full SmartCaseAI integration (LLM-based BDD generation) ✅
- [x] Full SmartLocatorAI integration (automatic locator generation) ✅
- [ ] Support for more BDD frameworks (Cucumber, SpecFlow)
- [ ] Visual mapping dashboard
- [ ] CI/CD integration templates
- [ ] Multi-language support (Java, JavaScript, C#)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Pydantic](https://pydantic.dev/) for data validation
- Integrates with [SmartCaseAI](https://github.com/shaktitrigent/Phoenix-SmartCaseAI) for LLM-powered BDD generation
- Integrates with [SmartLocatorAI](https://github.com/shaktitrigent/Phoenix-SmartLocatorAI) for automatic locator generation (using modular `dom_scanner` and `page_object_exporter` components)
- Uses [pytest-bdd](https://pytest-bdd.readthedocs.io/) for BDD test execution
- Uses [Playwright](https://playwright.dev/python/) and [Selenium](https://www.selenium.dev/) for web automation

---

**Made for QA Engineers who want to focus on what matters most** 🚀
