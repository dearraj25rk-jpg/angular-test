"""
Testing & Validation Agent
Handles testing, validation, and quality assurance during migration
"""

from crewai import Agent
from crewai_tools import FileReadTool, DirectoryReadTool
import subprocess
import os
import json
import re
from typing import Dict, List, Any


class TestingValidator:
    """Agent specialized in testing and validating Angular applications during migration"""

    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.directory_read_tool = DirectoryReadTool()

    def create_agent(self) -> Agent:
        return Agent(
            role="Angular Testing & Validation Specialist",
            goal="Ensure application functionality, performance, and quality during Angular migration",
            backstory="""You are an expert in Angular testing frameworks, quality assurance, and
            application validation. You specialize in running comprehensive test suites, analyzing
            build outputs, checking for performance regressions, and ensuring that migrations
            don't break existing functionality. You understand Jest, Karma, Jasmine, and modern
            Angular testing best practices.""",
            tools=[self.file_read_tool, self.directory_read_tool],
            verbose=True,
            allow_delegation=False
        )

    def run_comprehensive_tests(self, project_path: str) -> Dict[str, Any]:
        """Run all available tests and return comprehensive results"""
        test_results = {
            "unit_tests": {},
            "lint_check": {},
            "build_check": {},
            "format_check": {},
            "overall_status": "unknown",
            "recommendations": []
        }

        # Run unit tests
        test_results["unit_tests"] = self._run_unit_tests(project_path)

        # Run lint check
        test_results["lint_check"] = self._run_lint_check(project_path)

        # Run build check
        test_results["build_check"] = self._run_build_check(project_path)

        # Run format check
        test_results["format_check"] = self._run_format_check(project_path)

        # Determine overall status
        test_results["overall_status"] = self._determine_overall_status(test_results)

        # Generate recommendations
        test_results["recommendations"] = self._generate_recommendations(test_results)

        return test_results

    def _run_unit_tests(self, project_path: str) -> Dict[str, Any]:
        """Run unit tests using ng test"""
        try:
            # Check if karma config exists
            karma_config = os.path.join(project_path, "karma.conf.js")
            if not os.path.exists(karma_config):
                return {
                    "status": "skipped",
                    "reason": "Karma configuration not found"
                }

            # Run tests in headless mode
            result = subprocess.run(
                ["npm", "run", "test", "--", "--watch=false", "--browsers=ChromeHeadless"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse test results
            test_output = result.stdout + result.stderr
            test_summary = self._parse_test_output(test_output)

            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "summary": test_summary,
                "output": test_output[:2000],  # Limit output size
                "duration": self._extract_test_duration(test_output)
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Tests timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_lint_check(self, project_path: str) -> Dict[str, Any]:
        """Run ESLint checks"""
        try:
            # Check if lint script exists in package.json
            package_json_path = os.path.join(project_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    scripts = package_data.get('scripts', {})
                    if 'lint' not in scripts:
                        return {
                            "status": "skipped",
                            "reason": "Lint script not found in package.json"
                        }

            result = subprocess.run(
                ["npm", "run", "lint"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            lint_issues = self._parse_lint_output(result.stdout + result.stderr)

            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "issues": lint_issues,
                "output": (result.stdout + result.stderr)[:2000]
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Lint check timed out after 2 minutes"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_build_check(self, project_path: str) -> Dict[str, Any]:
        """Run production build check"""
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            build_info = self._parse_build_output(result.stdout + result.stderr)

            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "build_info": build_info,
                "output": (result.stdout + result.stderr)[:2000]
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Build timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_format_check(self, project_path: str) -> Dict[str, Any]:
        """Run Prettier format check"""
        try:
            # Check if format:check script exists
            package_json_path = os.path.join(project_path, "package.json")
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    scripts = package_data.get('scripts', {})
                    if 'format:check' not in scripts:
                        return {
                            "status": "skipped",
                            "reason": "Format check script not found"
                        }

            result = subprocess.run(
                ["npm", "run", "format:check"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            format_issues = self._parse_format_output(result.stdout + result.stderr)

            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "issues": format_issues,
                "output": (result.stdout + result.stderr)[:1000]
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Format check timed out after 1 minute"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse unit test output to extract summary"""
        summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_suites": 0
        }

        # Parse Karma/Jasmine output
        total_match = re.search(r"(\d+) tests? completed", output)
        if total_match:
            summary["total_tests"] = int(total_match.group(1))

        passed_match = re.search(r"(\d+) tests? passed", output)
        if passed_match:
            summary["passed"] = int(passed_match.group(1))

        failed_match = re.search(r"(\d+) tests? failed", output)
        if failed_match:
            summary["failed"] = int(failed_match.group(1))

        # Alternative pattern for different output formats
        if "TOTAL:" in output:
            total_line = re.search(r"TOTAL: (\d+) SUCCESS", output)
            if total_line:
                summary["passed"] = int(total_line.group(1))

        return summary

    def _parse_lint_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ESLint output to extract issues"""
        issues = []

        # Parse ESLint output format
        issue_pattern = r"(\S+):(\d+):(\d+):\s*(error|warning|info):\s*(.+)"
        matches = re.finditer(issue_pattern, output)

        for match in matches:
            issues.append({
                "file": match.group(1),
                "line": int(match.group(2)),
                "column": int(match.group(3)),
                "severity": match.group(4),
                "message": match.group(5).strip()
            })

        return issues

    def _parse_build_output(self, output: str) -> Dict[str, Any]:
        """Parse build output to extract information"""
        build_info = {
            "success": False,
            "chunks": [],
            "bundle_sizes": {},
            "warnings": [],
            "errors": []
        }

        if "Build at:" in output or "built at:" in output:
            build_info["success"] = True

        # Parse bundle information
        chunk_pattern = r"(\w+)\.js\s+(\d+(?:\.\d+)?)\s*(kB|MB)"
        chunks = re.finditer(chunk_pattern, output)
        for chunk in chunks:
            build_info["chunks"].append({
                "name": chunk.group(1),
                "size": chunk.group(2),
                "unit": chunk.group(3)
            })

        # Extract warnings and errors
        warning_lines = [line for line in output.split('\n') if 'WARNING' in line.upper()]
        error_lines = [line for line in output.split('\n') if 'ERROR' in line.upper()]

        build_info["warnings"] = warning_lines[:5]  # Limit to first 5
        build_info["errors"] = error_lines[:5]  # Limit to first 5

        return build_info

    def _parse_format_output(self, output: str) -> List[str]:
        """Parse Prettier format check output"""
        if "Code style issues found" in output or "would be reformatted" in output:
            # Extract file names that need formatting
            files = re.findall(r"(\S+\.(?:ts|js|html|scss|css))", output)
            return list(set(files))  # Remove duplicates
        return []

    def _extract_test_duration(self, output: str) -> str:
        """Extract test execution duration"""
        duration_patterns = [
            r"Executed \d+ of \d+ SUCCESS \((\d+\.\d+) secs\)",
            r"Time: (\d+\.\d+)s",
            r"in (\d+\.\d+)s"
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, output)
            if match:
                return f"{match.group(1)}s"

        return "unknown"

    def _determine_overall_status(self, test_results: Dict) -> str:
        """Determine overall status based on all test results"""
        statuses = [
            test_results["unit_tests"].get("status", "unknown"),
            test_results["lint_check"].get("status", "unknown"),
            test_results["build_check"].get("status", "unknown"),
            test_results["format_check"].get("status", "unknown")
        ]

        if any(status == "failed" for status in statuses):
            return "failed"
        elif any(status == "error" for status in statuses):
            return "error"
        elif any(status == "timeout" for status in statuses):
            return "timeout"
        elif all(status in ["passed", "skipped"] for status in statuses):
            return "passed"
        else:
            return "partial"

    def _generate_recommendations(self, test_results: Dict) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Unit test recommendations
        unit_status = test_results["unit_tests"].get("status")
        if unit_status == "failed":
            recommendations.append("Fix failing unit tests before proceeding with migration")
        elif unit_status == "skipped":
            recommendations.append("Consider setting up unit tests for better migration validation")

        # Lint recommendations
        lint_status = test_results["lint_check"].get("status")
        if lint_status == "failed":
            lint_issues = len(test_results["lint_check"].get("issues", []))
            recommendations.append(f"Fix {lint_issues} linting issues for better code quality")

        # Build recommendations
        build_status = test_results["build_check"].get("status")
        if build_status == "failed":
            recommendations.append("Resolve build errors before completing migration")
        elif build_status == "passed":
            build_info = test_results["build_check"].get("build_info", {})
            if build_info.get("warnings"):
                recommendations.append("Review build warnings for potential issues")

        # Format recommendations
        format_status = test_results["format_check"].get("status")
        if format_status == "failed":
            format_issues = len(test_results["format_check"].get("issues", []))
            recommendations.append(f"Format {format_issues} files using 'npm run format'")

        if not recommendations:
            recommendations.append("All checks passed! Migration validation successful.")

        return recommendations

    def validate_angular_specific_features(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Validate Angular-specific features work correctly after migration"""
        validation_results = {
            "routing_check": self._validate_routing(project_path),
            "service_injection": self._validate_services(project_path),
            "component_lifecycle": self._validate_components(project_path),
            "module_structure": self._validate_modules(project_path),
            "overall_status": "unknown"
        }

        # Determine overall validation status
        all_checks = [validation_results[key] for key in validation_results if key != "overall_status"]
        if all(check.get("status") == "passed" for check in all_checks):
            validation_results["overall_status"] = "passed"
        elif any(check.get("status") == "failed" for check in all_checks):
            validation_results["overall_status"] = "failed"
        else:
            validation_results["overall_status"] = "partial"

        return validation_results

    def _validate_routing(self, project_path: str) -> Dict[str, Any]:
        """Validate Angular routing configuration"""
        try:
            routing_files = []
            src_path = os.path.join(project_path, "src")

            # Find routing files
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if "routing" in file and file.endswith(".ts"):
                        routing_files.append(os.path.join(root, file))

            if not routing_files:
                return {"status": "skipped", "reason": "No routing files found"}

            issues = []
            for routing_file in routing_files:
                with open(routing_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for common routing issues
                    if "RouterModule.forRoot" in content and "{ enableTracing: true }" in content:
                        issues.append("Production routing should not have enableTracing enabled")

                    if "loadChildren:" in content and "() => import" not in content:
                        issues.append("Lazy loading should use dynamic imports")

            return {
                "status": "passed" if not issues else "failed",
                "files_checked": len(routing_files),
                "issues": issues
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _validate_services(self, project_path: str) -> Dict[str, Any]:
        """Validate Angular services"""
        try:
            service_files = []
            src_path = os.path.join(project_path, "src")

            # Find service files
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(".service.ts"):
                        service_files.append(os.path.join(root, file))

            if not service_files:
                return {"status": "skipped", "reason": "No service files found"}

            issues = []
            for service_file in service_files:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for proper dependency injection
                    if "@Injectable" not in content:
                        issues.append(f"Service {service_file} missing @Injectable decorator")

                    # Check for deprecated HTTP usage
                    if "import { Http }" in content:
                        issues.append(f"Service {service_file} uses deprecated Http instead of HttpClient")

            return {
                "status": "passed" if not issues else "failed",
                "files_checked": len(service_files),
                "issues": issues
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _validate_components(self, project_path: str) -> Dict[str, Any]:
        """Validate Angular components"""
        try:
            component_files = []
            src_path = os.path.join(project_path, "src")

            # Find component files
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(".component.ts"):
                        component_files.append(os.path.join(root, file))

            if not component_files:
                return {"status": "skipped", "reason": "No component files found"}

            issues = []
            for component_file in component_files:
                with open(component_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for proper component structure
                    if "@Component" not in content:
                        issues.append(f"Component {component_file} missing @Component decorator")

                    # Check for deprecated lifecycle hooks
                    if "ngOnInit" in content and "OnInit" not in content:
                        issues.append(f"Component {component_file} implements ngOnInit but doesn't import OnInit")

            return {
                "status": "passed" if not issues else "failed",
                "files_checked": len(component_files),
                "issues": issues
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _validate_modules(self, project_path: str) -> Dict[str, Any]:
        """Validate Angular modules"""
        try:
            module_files = []
            src_path = os.path.join(project_path, "src")

            # Find module files
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(".module.ts"):
                        module_files.append(os.path.join(root, file))

            if not module_files:
                return {"status": "skipped", "reason": "No module files found (possibly using standalone components)"}

            issues = []
            for module_file in module_files:
                with open(module_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for proper module structure
                    if "@NgModule" not in content:
                        issues.append(f"Module {module_file} missing @NgModule decorator")

                    # Check for deprecated module imports
                    if "HttpModule" in content:
                        issues.append(f"Module {module_file} uses deprecated HttpModule")

            return {
                "status": "passed" if not issues else "failed",
                "files_checked": len(module_files),
                "issues": issues
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}