"""
Angular Migration Crew
Main orchestration script for Angular migration using CrewAI
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from crewai import Crew, Task, Process
from langchain_openai import ChatOpenAI

# Import our specialized agents
from agents.migration_analyzer import AngularMigrationAnalyzer
from agents.dependency_manager import DependencyManager
from agents.code_transformer import CodeTransformer
from agents.testing_validator import TestingValidator
from agents.migration_coordinator import MigrationCoordinator

# Import MCPs
from mcps.angular_cli_mcp import AngularCLIMCP
from mcps.npm_mcp import NPMMCP


class AngularMigrationCrew:
    """
    Main orchestration class for Angular migration using CrewAI
    """

    def __init__(self, project_path: str, openai_api_key: str = None):
        self.project_path = os.path.abspath(project_path)
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')

        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )

        # Initialize agents
        self.migration_analyzer = AngularMigrationAnalyzer()
        self.dependency_manager = DependencyManager()
        self.code_transformer = CodeTransformer()
        self.testing_validator = TestingValidator()
        self.migration_coordinator = MigrationCoordinator()

        # Initialize MCPs
        self.angular_cli_mcp = AngularCLIMCP(self.project_path)
        self.npm_mcp = NPMMCP(self.project_path)

        # Create crew agents
        self.agents = {
            "analyzer": self.migration_analyzer.create_agent(),
            "dependency_manager": self.dependency_manager.create_agent(),
            "code_transformer": self.code_transformer.create_agent(),
            "testing_validator": self.testing_validator.create_agent(),
            "coordinator": self.migration_coordinator.create_agent()
        }

        # Set LLM for all agents
        for agent in self.agents.values():
            agent.llm = self.llm

    def create_migration_tasks(self, target_version: str, options: Dict[str, Any] = None) -> List[Task]:
        """Create tasks for the migration process"""
        if options is None:
            options = {}

        tasks = []

        # Task 1: Analyze current project
        analyze_task = Task(
            description=f"""
            Analyze the Angular project at {self.project_path} and determine migration requirements
            for upgrading to Angular {target_version}.

            Requirements:
            1. Identify current Angular version and all dependencies
            2. Scan for deprecated APIs and features
            3. Generate migration roadmap with estimated effort
            4. Identify potential blocking issues
            5. Create comprehensive analysis report

            Output: Detailed analysis report in JSON format
            """,
            agent=self.agents["analyzer"],
            expected_output="JSON analysis report with current version, deprecated features, roadmap, and recommendations"
        )
        tasks.append(analyze_task)

        # Task 2: Pre-migration testing
        pre_test_task = Task(
            description=f"""
            Run comprehensive pre-migration tests to establish baseline for the Angular project.

            Requirements:
            1. Execute unit tests and record results
            2. Run linting and format checks
            3. Verify production build works
            4. Validate current Angular functionality
            5. Document any existing issues

            Output: Pre-migration test report with baseline metrics
            """,
            agent=self.agents["testing_validator"],
            expected_output="Test report with unit test results, build status, lint results, and baseline metrics",
            context=[analyze_task]
        )
        tasks.append(pre_test_task)

        # Task 3: Update dependencies
        dependency_task = Task(
            description=f"""
            Update project dependencies for Angular {target_version} migration.

            Requirements:
            1. Backup current package.json
            2. Update Angular packages to version {target_version}
            3. Update compatible versions of other dependencies
            4. Install updated dependencies
            5. Validate dependency installation
            6. Resolve any compatibility conflicts

            Output: Dependency update report with changes made and validation results
            """,
            agent=self.agents["dependency_manager"],
            expected_output="Dependency update report with package changes, installation status, and validation results",
            context=[analyze_task, pre_test_task]
        )
        tasks.append(dependency_task)

        # Task 4: Transform code
        transform_task = Task(
            description=f"""
            Transform application code for Angular {target_version} compatibility.

            Requirements:
            1. Update deprecated import statements
            2. Migrate to new APIs where applicable
            3. Convert to standalone components if beneficial (Angular 14+)
            4. Apply control flow syntax updates (Angular 18+)
            5. Update template syntax and directives
            6. Ensure code follows modern Angular patterns

            Output: Code transformation report with files modified and changes applied
            """,
            agent=self.agents["code_transformer"],
            expected_output="Code transformation report with list of modified files and applied changes",
            context=[analyze_task, dependency_task]
        )
        tasks.append(transform_task)

        # Task 5: Post-migration testing
        post_test_task = Task(
            description=f"""
            Run comprehensive post-migration tests to validate the upgrade to Angular {target_version}.

            Requirements:
            1. Execute full test suite (unit tests, linting, build)
            2. Validate Angular-specific functionality
            3. Compare results with pre-migration baseline
            4. Identify any new issues or regressions
            5. Verify application functionality

            Output: Post-migration test report with comparison to baseline and issue identification
            """,
            agent=self.agents["testing_validator"],
            expected_output="Post-migration test report with test results, comparisons, and identified issues",
            context=[analyze_task, dependency_task, transform_task]
        )
        tasks.append(post_test_task)

        # Task 6: Final validation and coordination
        final_task = Task(
            description=f"""
            Coordinate final validation and provide comprehensive migration summary.

            Requirements:
            1. Validate Angular version matches target {target_version}
            2. Ensure production build succeeds
            3. Verify migration completeness
            4. Generate final migration report
            5. Provide recommendations for next steps
            6. Document any remaining issues

            Output: Final migration report with status, recommendations, and next steps
            """,
            agent=self.agents["coordinator"],
            expected_output="Final migration report with overall status, validation results, and recommendations",
            context=[analyze_task, pre_test_task, dependency_task, transform_task, post_test_task]
        )
        tasks.append(final_task)

        return tasks

    async def execute_migration(self, target_version: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the complete Angular migration process"""
        if options is None:
            options = {}

        print(f"Starting Angular migration to version {target_version}")
        print(f"Project path: {self.project_path}")

        start_time = datetime.now()
        migration_id = f"migration_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # Validate project
            if not self._validate_project():
                return {
                    "success": False,
                    "error": "Invalid Angular project structure"
                }

            # Create tasks
            tasks = self.create_migration_tasks(target_version, options)

            # Create crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )

            # Execute migration
            print("Executing migration tasks...")
            result = crew.kickoff()

            # Process results
            end_time = datetime.now()
            duration = end_time - start_time

            migration_result = {
                "migration_id": migration_id,
                "success": True,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(duration),
                "target_version": target_version,
                "project_path": self.project_path,
                "options": options,
                "result": str(result),
                "tasks_completed": len(tasks)
            }

            # Save migration log
            self._save_migration_log(migration_result)

            print(f"Migration completed successfully in {duration}")
            return migration_result

        except Exception as e:
            end_time = datetime.now()
            duration = end_time - start_time

            error_result = {
                "migration_id": migration_id,
                "success": False,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": str(duration),
                "target_version": target_version,
                "project_path": self.project_path,
                "error": str(e)
            }

            self._save_migration_log(error_result)
            print(f"Migration failed: {str(e)}")
            return error_result

    def _validate_project(self) -> bool:
        """Validate that the project is a valid Angular project"""
        required_files = ["package.json", "angular.json"]

        for file in required_files:
            if not os.path.exists(os.path.join(self.project_path, file)):
                print(f"Missing required file: {file}")
                return False

        # Check if it's an Angular project
        package_json_path = os.path.join(self.project_path, "package.json")
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            angular_core = dependencies.get('@angular/core') or dev_dependencies.get('@angular/core')
            if not angular_core:
                print("Not an Angular project (no @angular/core dependency found)")
                return False

            print(f"Valid Angular project detected (current version: {angular_core})")
            return True

        except Exception as e:
            print(f"Error validating project: {str(e)}")
            return False

    def _save_migration_log(self, migration_result: Dict[str, Any]):
        """Save migration log to file"""
        logs_dir = os.path.join(self.project_path, "migration_logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_file = os.path.join(logs_dir, f"{migration_result['migration_id']}.json")
        with open(log_file, 'w') as f:
            json.dump(migration_result, f, indent=2)

        print(f"Migration log saved to: {log_file}")

    async def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        try:
            # Get Angular version
            ng_version = await self.angular_cli_mcp.call_tool("ng_version", {})

            # Get package info
            package_info = await self.npm_mcp.call_tool("package_json_info", {})

            # Get dependency audit
            audit_info = await self.npm_mcp.call_tool("npm_audit", {})

            # Get outdated packages
            outdated_info = await self.npm_mcp.call_tool("npm_outdated", {})

            return {
                "success": True,
                "angular_info": ng_version.get("version_info", {}),
                "package_info": package_info.get("package_info", {}),
                "security_audit": audit_info.get("audit_info", {}),
                "outdated_packages": outdated_info.get("outdated_info", {}),
                "project_path": self.project_path
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def run_tests(self) -> Dict[str, Any]:
        """Run project tests using MCPs"""
        try:
            # Run Angular tests
            test_result = await self.angular_cli_mcp.call_tool("ng_test", {
                "watch": False,
                "browsers": "ChromeHeadless"
            })

            # Run lint
            lint_result = await self.angular_cli_mcp.call_tool("ng_lint", {})

            # Run build
            build_result = await self.angular_cli_mcp.call_tool("ng_build", {
                "configuration": "production"
            })

            return {
                "success": True,
                "test_results": test_result,
                "lint_results": lint_result,
                "build_results": build_result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """Main entry point for the Angular Migration Crew"""
    import argparse

    parser = argparse.ArgumentParser(description="Angular Migration Crew - Automated Angular Upgrades")
    parser.add_argument("--project-path", "-p", default=".", help="Path to Angular project")
    parser.add_argument("--target-version", "-t", required=True, help="Target Angular version (e.g., 20.3.0)")
    parser.add_argument("--openai-api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--skip-failing-tests", action="store_true", help="Continue migration even if tests fail")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only, don't make changes")
    parser.add_argument("--status", action="store_true", help="Get project status only")

    args = parser.parse_args()

    try:
        # Initialize migration crew
        crew = AngularMigrationCrew(
            project_path=args.project_path,
            openai_api_key=args.openai_api_key
        )

        if args.status:
            # Get project status
            async def get_status():
                status = await crew.get_project_status()
                print(json.dumps(status, indent=2))

            asyncio.run(get_status())
            return

        # Execute migration
        options = {
            "skip_failing_tests": args.skip_failing_tests,
            "dry_run": args.dry_run
        }

        async def run_migration():
            result = await crew.execute_migration(args.target_version, options)
            print("\n" + "="*50)
            print("MIGRATION SUMMARY")
            print("="*50)
            print(f"Success: {result['success']}")
            print(f"Duration: {result.get('duration', 'Unknown')}")

            if result['success']:
                print(f"Successfully migrated to Angular {args.target_version}")
            else:
                print(f"Migration failed: {result.get('error', 'Unknown error')}")

        asyncio.run(run_migration())

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()