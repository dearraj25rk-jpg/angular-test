"""
Migration Coordinator Agent
Orchestrates the entire Angular migration process and coordinates between other agents
"""

from crewai import Agent
from crewai_tools import FileReadTool, FileWriteTool, DirectoryReadTool
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from .migration_analyzer import AngularMigrationAnalyzer
from .dependency_manager import DependencyManager
from .code_transformer import CodeTransformer
from .testing_validator import TestingValidator


class MigrationCoordinator:
    """Master agent that coordinates the entire Angular migration process"""

    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.file_write_tool = FileWriteTool()
        self.directory_read_tool = DirectoryReadTool()

        # Initialize specialized agents
        self.analyzer = AngularMigrationAnalyzer()
        self.dependency_manager = DependencyManager()
        self.code_transformer = CodeTransformer()
        self.testing_validator = TestingValidator()

    def create_agent(self) -> Agent:
        return Agent(
            role="Angular Migration Coordinator",
            goal="Orchestrate and coordinate the entire Angular migration process from analysis to completion",
            backstory="""You are the master coordinator for Angular migrations with extensive experience
            in large-scale application upgrades. You understand the complexities of coordinating multiple
            migration tasks, managing dependencies between different phases, and ensuring successful
            completion of complex Angular version upgrades. You excel at planning, risk management,
            and ensuring quality throughout the migration process.""",
            tools=[self.file_read_tool, self.file_write_tool, self.directory_read_tool],
            verbose=True,
            allow_delegation=True
        )

    def execute_migration(self, project_path: str, target_version: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the complete Angular migration process"""
        if options is None:
            options = {}

        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        migration_log = {
            "migration_id": migration_id,
            "start_time": datetime.now().isoformat(),
            "project_path": project_path,
            "target_version": target_version,
            "options": options,
            "phases": {},
            "overall_status": "in_progress",
            "end_time": None
        }

        try:
            # Phase 1: Analysis
            print(f"Phase 1: Analyzing project for migration to Angular {target_version}")
            analysis_result = self._execute_analysis_phase(project_path, target_version)
            migration_log["phases"]["analysis"] = analysis_result

            if not analysis_result["success"]:
                migration_log["overall_status"] = "failed"
                migration_log["failure_reason"] = "Analysis phase failed"
                return migration_log

            # Phase 2: Pre-migration Testing
            print("Phase 2: Running pre-migration tests")
            pre_test_result = self._execute_pre_migration_testing(project_path)
            migration_log["phases"]["pre_migration_testing"] = pre_test_result

            if not pre_test_result["success"] and not options.get("skip_failing_tests", False):
                migration_log["overall_status"] = "failed"
                migration_log["failure_reason"] = "Pre-migration tests failed"
                return migration_log

            # Phase 3: Dependency Updates
            print("Phase 3: Updating dependencies")
            dependency_result = self._execute_dependency_phase(project_path, target_version)
            migration_log["phases"]["dependency_update"] = dependency_result

            if not dependency_result["success"]:
                migration_log["overall_status"] = "failed"
                migration_log["failure_reason"] = "Dependency update failed"
                return migration_log

            # Phase 4: Code Transformation
            print("Phase 4: Transforming code")
            transformation_result = self._execute_transformation_phase(project_path, target_version)
            migration_log["phases"]["code_transformation"] = transformation_result

            # Phase 5: Post-migration Testing
            print("Phase 5: Running post-migration tests")
            post_test_result = self._execute_post_migration_testing(project_path, target_version)
            migration_log["phases"]["post_migration_testing"] = post_test_result

            # Phase 6: Final Validation
            print("Phase 6: Final validation")
            validation_result = self._execute_final_validation(project_path, target_version)
            migration_log["phases"]["final_validation"] = validation_result

            # Determine overall success
            migration_log["overall_status"] = self._determine_migration_success(migration_log["phases"])
            migration_log["end_time"] = datetime.now().isoformat()

            # Save migration log
            self._save_migration_log(project_path, migration_log)

            return migration_log

        except Exception as e:
            migration_log["overall_status"] = "error"
            migration_log["error"] = str(e)
            migration_log["end_time"] = datetime.now().isoformat()
            return migration_log

    def _execute_analysis_phase(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Execute the analysis phase"""
        try:
            analysis = self.analyzer.analyze_project_structure(project_path)

            # Extract current version
            current_version = analysis.get("package_json_analysis", {}).get("angular_core_version", "unknown")

            # Generate migration roadmap
            roadmap = self.analyzer.get_migration_roadmap(current_version, target_version)

            # Check for blocking issues
            blocking_issues = []
            if analysis.get("deprecated_features"):
                critical_deprecated = [f for f in analysis["deprecated_features"] if f.get("severity") == "high"]
                if critical_deprecated:
                    blocking_issues.extend([f["pattern"] for f in critical_deprecated])

            return {
                "success": True,
                "current_version": current_version,
                "target_version": target_version,
                "analysis": analysis,
                "roadmap": roadmap,
                "blocking_issues": blocking_issues,
                "estimated_duration": self._estimate_migration_duration(analysis, roadmap)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_pre_migration_testing(self, project_path: str) -> Dict[str, Any]:
        """Execute pre-migration testing"""
        try:
            test_results = self.testing_validator.run_comprehensive_tests(project_path)

            return {
                "success": test_results["overall_status"] in ["passed", "partial"],
                "test_results": test_results,
                "critical_failures": self._identify_critical_test_failures(test_results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_dependency_phase(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Execute dependency update phase"""
        try:
            # Analyze current dependencies
            dep_analysis = self.dependency_manager.analyze_dependencies(project_path)

            # Create backup of package.json
            self._backup_package_json(project_path)

            # Update package.json
            package_update = self.dependency_manager.create_migration_package_json(project_path, target_version)

            if not package_update["success"]:
                return {
                    "success": False,
                    "error": package_update["error"]
                }

            # Write updated package.json
            package_json_path = os.path.join(project_path, "package.json")
            with open(package_json_path, 'w') as f:
                json.dump(package_update["updated_package_json"], f, indent=2)

            # Install dependencies
            install_result = self.dependency_manager.execute_dependency_update(project_path, "npm install")

            # Validate installation
            validation = self.dependency_manager.validate_dependencies(project_path)

            return {
                "success": install_result["success"] and validation["valid"],
                "dependency_analysis": dep_analysis,
                "package_changes": package_update.get("changes", []),
                "install_result": install_result,
                "validation": validation
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_transformation_phase(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Execute code transformation phase"""
        try:
            # Analyze code changes needed
            transformation_analysis = self.code_transformer.analyze_code_changes_needed(project_path, target_version)

            applied_transformations = []
            transformation_errors = []

            # Apply transformations to each file
            for file_info in transformation_analysis.get("files_to_transform", []):
                file_path = file_info["file"]
                transformations = file_info["transformations"]

                result = self.code_transformer.apply_transformations(file_path, transformations)

                if result["success"]:
                    applied_transformations.extend(result["applied_transformations"])
                else:
                    transformation_errors.append({
                        "file": file_path,
                        "error": result["error"]
                    })

            # Special transformations for Angular 18+
            if int(target_version.split('.')[0]) >= 18:
                # Convert components to standalone if beneficial
                self._apply_standalone_conversions(project_path, target_version)

                # Migrate to control flow syntax
                self._apply_control_flow_migrations(project_path)

            return {
                "success": len(transformation_errors) == 0,
                "transformation_analysis": transformation_analysis,
                "applied_transformations": applied_transformations,
                "transformation_errors": transformation_errors,
                "total_files_transformed": len(applied_transformations)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_post_migration_testing(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Execute post-migration testing"""
        try:
            # Run comprehensive tests
            test_results = self.testing_validator.run_comprehensive_tests(project_path)

            # Run Angular-specific validation
            angular_validation = self.testing_validator.validate_angular_specific_features(project_path, target_version)

            return {
                "success": test_results["overall_status"] in ["passed", "partial"],
                "test_results": test_results,
                "angular_validation": angular_validation,
                "new_failures": self._compare_test_results(test_results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_final_validation(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Execute final migration validation"""
        try:
            validation_results = {
                "version_check": self._validate_angular_version(project_path, target_version),
                "build_validation": self._validate_production_build(project_path),
                "performance_check": self._check_performance_impact(project_path),
                "migration_completeness": self._check_migration_completeness(project_path, target_version)
            }

            overall_success = all(check.get("success", False) for check in validation_results.values())

            return {
                "success": overall_success,
                "validation_results": validation_results,
                "recommendations": self._generate_final_recommendations(validation_results)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _backup_package_json(self, project_path: str):
        """Create backup of package.json"""
        package_json_path = os.path.join(project_path, "package.json")
        backup_path = os.path.join(project_path, f"package.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        with open(package_json_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())

    def _apply_standalone_conversions(self, project_path: str, target_version: str):
        """Apply standalone component conversions"""
        src_path = os.path.join(project_path, "src")
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(".component.ts"):
                    file_path = os.path.join(root, file)
                    self.code_transformer.convert_to_standalone_component(file_path)

    def _apply_control_flow_migrations(self, project_path: str):
        """Apply control flow syntax migrations"""
        src_path = os.path.join(project_path, "src")
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(".component.html"):
                    file_path = os.path.join(root, file)
                    self.code_transformer.migrate_control_flow_syntax(file_path)

    def _validate_angular_version(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Validate that Angular version matches target"""
        try:
            package_json_path = os.path.join(project_path, "package.json")
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            angular_core_version = package_data.get("dependencies", {}).get("@angular/core", "")
            target_major = target_version.split('.')[0]

            success = target_major in angular_core_version

            return {
                "success": success,
                "current_version": angular_core_version,
                "target_version": target_version,
                "matches": success
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_production_build(self, project_path: str) -> Dict[str, Any]:
        """Validate production build works"""
        try:
            build_result = self.testing_validator._run_build_check(project_path)
            return {
                "success": build_result["status"] == "passed",
                "build_result": build_result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_performance_impact(self, project_path: str) -> Dict[str, Any]:
        """Check for performance impact of migration"""
        # This is a placeholder for performance analysis
        return {
            "success": True,
            "message": "Performance impact analysis not implemented"
        }

    def _check_migration_completeness(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Check if migration is complete"""
        try:
            analysis = self.analyzer.analyze_project_structure(project_path)
            deprecated_features = analysis.get("deprecated_features", [])

            incomplete_items = [f for f in deprecated_features if f.get("severity") == "high"]

            return {
                "success": len(incomplete_items) == 0,
                "incomplete_items": incomplete_items,
                "total_deprecated": len(deprecated_features)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _estimate_migration_duration(self, analysis: Dict, roadmap: List) -> str:
        """Estimate migration duration"""
        base_time = len(roadmap) * 2  # 2 hours per version step
        deprecated_count = len(analysis.get("deprecated_features", []))

        if deprecated_count > 20:
            base_time += 4
        elif deprecated_count > 10:
            base_time += 2

        return f"{base_time}-{base_time + 2} hours"

    def _identify_critical_test_failures(self, test_results: Dict) -> List[str]:
        """Identify critical test failures"""
        critical_failures = []

        if test_results["build_check"].get("status") == "failed":
            critical_failures.append("Build failure")

        unit_test_status = test_results["unit_tests"].get("status")
        if unit_test_status == "failed":
            summary = test_results["unit_tests"].get("summary", {})
            failed_count = summary.get("failed", 0)
            if failed_count > 0:
                critical_failures.append(f"{failed_count} unit tests failing")

        return critical_failures

    def _compare_test_results(self, current_results: Dict) -> List[str]:
        """Compare current test results with previous ones"""
        # This would require storing previous test results
        # For now, return empty list
        return []

    def _determine_migration_success(self, phases: Dict) -> str:
        """Determine overall migration success"""
        critical_phases = ["analysis", "dependency_update", "final_validation"]

        for phase_name in critical_phases:
            phase = phases.get(phase_name, {})
            if not phase.get("success", False):
                return "failed"

        # Check if all phases succeeded
        all_successful = all(phase.get("success", False) for phase in phases.values())

        if all_successful:
            return "completed"
        else:
            return "partial"

    def _generate_final_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate final recommendations"""
        recommendations = []

        for check_name, result in validation_results.items():
            if not result.get("success", False):
                if check_name == "version_check":
                    recommendations.append("Verify Angular version alignment in package.json")
                elif check_name == "build_validation":
                    recommendations.append("Fix production build issues")
                elif check_name == "migration_completeness":
                    incomplete = len(result.get("incomplete_items", []))
                    recommendations.append(f"Address {incomplete} remaining migration items")

        if not recommendations:
            recommendations.append("Migration completed successfully! Consider updating documentation.")

        return recommendations

    def _save_migration_log(self, project_path: str, migration_log: Dict):
        """Save migration log to file"""
        log_dir = os.path.join(project_path, "migration_logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"{migration_log['migration_id']}.json")
        with open(log_file, 'w') as f:
            json.dump(migration_log, f, indent=2)

    def get_migration_status(self, project_path: str, migration_id: str = None) -> Dict[str, Any]:
        """Get status of a migration"""
        log_dir = os.path.join(project_path, "migration_logs")

        if migration_id:
            log_file = os.path.join(log_dir, f"{migration_id}.json")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return json.load(f)
            else:
                return {"error": "Migration log not found"}
        else:
            # Return latest migration
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
                if log_files:
                    latest_log = sorted(log_files)[-1]
                    with open(os.path.join(log_dir, latest_log), 'r') as f:
                        return json.load(f)

            return {"error": "No migration logs found"}