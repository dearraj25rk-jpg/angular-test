# Angular Migration Crew

A comprehensive CrewAI-based system for automating Angular application migrations from version 17 to 20.3.0 and beyond.

## Overview

This system uses multiple specialized AI agents to handle different aspects of Angular migrations:

- **Migration Analyzer**: Analyzes project structure and identifies migration requirements
- **Dependency Manager**: Handles package updates and version compatibility
- **Code Transformer**: Transforms code to use new APIs and syntax
- **Testing Validator**: Runs tests and validates functionality
- **Migration Coordinator**: Orchestrates the entire process

## Features

- Automated Angular version detection and analysis
- Comprehensive dependency management
- Code transformation for new Angular features
- Pre and post-migration testing
- Angular CLI integration via MCPs
- NPM package management via MCPs
- Detailed migration logging and reporting
- Support for Angular 18+ control flow syntax
- Standalone component conversion
- Security audit and vulnerability checking

## Installation

1. Install Python dependencies:
```bash
cd crew_agents
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Migration

```bash
# Migrate to Angular 20.3.0
python angular_migration_crew.py --target-version 20.3.0

# Migrate with custom project path
python angular_migration_crew.py --project-path /path/to/project --target-version 20.3.0
```

### Advanced Options

```bash
# Continue migration even if tests fail
python angular_migration_crew.py --target-version 20.3.0 --skip-failing-tests

# Dry run (analysis only, no changes)
python angular_migration_crew.py --target-version 20.3.0 --dry-run

# Get project status
python angular_migration_crew.py --status
```

## Architecture

### Agents

1. **AngularMigrationAnalyzer** (`agents/migration_analyzer.py`)
   - Analyzes current Angular version and dependencies
   - Identifies deprecated features and breaking changes
   - Generates migration roadmap

2. **DependencyManager** (`agents/dependency_manager.py`)
   - Updates package.json with compatible versions
   - Manages npm installations and updates
   - Resolves dependency conflicts

3. **CodeTransformer** (`agents/code_transformer.py`)
   - Updates deprecated import statements
   - Converts to standalone components
   - Applies control flow syntax (Angular 18+)
   - Transforms templates and components

4. **TestingValidator** (`agents/testing_validator.py`)
   - Runs unit tests, linting, and builds
   - Validates Angular-specific functionality
   - Compares pre and post-migration results

5. **MigrationCoordinator** (`agents/migration_coordinator.py`)
   - Orchestrates the entire migration process
   - Manages task dependencies and sequencing
   - Provides comprehensive reporting

### MCPs (Model Context Protocol)

1. **AngularCLIMCP** (`mcps/angular_cli_mcp.py`)
   - Provides Angular CLI integration
   - Commands: `ng version`, `ng update`, `ng build`, `ng test`, `ng lint`

2. **NPMMCP** (`mcps/npm_mcp.py`)
   - Provides npm package management
   - Commands: `npm install`, `npm audit`, `npm outdated`, `npm run`

## Migration Process

The migration follows a 6-phase process:

1. **Analysis Phase**
   - Project structure analysis
   - Current version detection
   - Deprecated feature identification
   - Migration roadmap generation

2. **Pre-migration Testing**
   - Baseline test execution
   - Build validation
   - Linting checks
   - Current functionality verification

3. **Dependency Updates**
   - Package.json backup
   - Angular package updates
   - Dependency installation
   - Compatibility validation

4. **Code Transformation**
   - Import statement updates
   - API migration
   - Standalone component conversion
   - Control flow syntax updates

5. **Post-migration Testing**
   - Full test suite execution
   - Angular-specific validation
   - Regression identification
   - Functionality verification

6. **Final Validation**
   - Version verification
   - Production build validation
   - Migration completeness check
   - Final reporting

## Output

The system generates comprehensive logs and reports:

- **Migration Logs**: Stored in `migration_logs/` directory
- **JSON Reports**: Detailed results for each phase
- **Status Reports**: Current project status and recommendations
- **Error Tracking**: Detailed error information and suggestions

## Example Migration Log

```json
{
  "migration_id": "migration_20241226_143052",
  "success": true,
  "start_time": "2024-12-26T14:30:52",
  "end_time": "2024-12-26T14:45:18",
  "duration": "0:14:26",
  "target_version": "20.3.0",
  "tasks_completed": 6,
  "phases": {
    "analysis": {
      "success": true,
      "current_version": "17",
      "deprecated_features": [...],
      "roadmap": [...]
    },
    "dependency_update": {
      "success": true,
      "packages_updated": 15,
      "conflicts_resolved": 2
    },
    // ... other phases
  }
}
```

## Supported Angular Versions

- **Source**: Angular 17+
- **Target**: Angular 18, 19, 20.3.0
- **Features**:
  - Angular 18+ control flow syntax
  - Standalone components (14+)
  - Modern Angular patterns

## Requirements

- Python 3.8+
- Node.js 18+
- Angular CLI
- OpenAI API key
- Valid Angular project structure

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

2. **Angular CLI Not Found**
   ```bash
   npm install -g @angular/cli
   ```

3. **Test Failures**
   ```bash
   # Use skip-failing-tests flag
   python angular_migration_crew.py --target-version 20.3.0 --skip-failing-tests
   ```

### Getting Help

1. Check migration logs in `migration_logs/`
2. Run status check: `python angular_migration_crew.py --status`
3. Use dry-run mode: `python angular_migration_crew.py --target-version 20.3.0 --dry-run`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.