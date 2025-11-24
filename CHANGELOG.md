# Changelog

All notable changes to Phoenix-SmartFusionAI will be documented in this file.

## [1.0.0] - 2025-01-XX

### Added
- **Locator Parser**: Parse `page.py` and `locators.json` files to extract locator information
- **BDD Generator**: Generate and parse BDD feature files from user stories
- **Fusion Mapper**: Core engine that maps BDD steps to locator variables
  - Exact matching for tokens
  - Partial matching support
  - Token extraction from step text
  - Step rewriting with locator variables
- **Step Definition Generator**: Auto-generate Python step definitions for:
  - Playwright framework
  - Selenium framework
- **Output Exporter**: Export enhanced features, step definitions, and reports
- **Main Pipeline**: End-to-end pipeline script with CLI interface
- **Pydantic Models**: Type-safe data models for all components
- **Unit Tests**: Test suite for core components
- **Examples**: Example files demonstrating usage
- **Documentation**: Comprehensive README and Quick Start guide

### Features
- Support for both Playwright and Selenium frameworks
- Intelligent token extraction and matching
- Traceability mapping reports
- Enhanced BDD feature files with embedded locator references
- Configurable strict mode for unmatched locators
- Partial matching for flexible locator mapping

### Architecture
- Modular design with separate engines for each component
- Extensible architecture for future enhancements
- Clean separation of concerns
- Type-safe with Pydantic models

