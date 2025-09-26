"""
Dependency Manager Agent
Handles package updates, version compatibility, and dependency resolution
"""

from crewai import Agent
from crewai_tools import FileReadTool, FileWriteTool, DirectoryReadTool
import json
import subprocess
import re
from typing import Dict, List, Any, Tuple
import os


class DependencyManager:
    """Agent specialized in managing Angular project dependencies during migration"""

    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.file_write_tool = FileWriteTool()
        self.directory_read_tool = DirectoryReadTool()

    def create_agent(self) -> Agent:
        return Agent(
            role="Angular Dependency Manager",
            goal="Manage and update Angular project dependencies during migration, ensuring compatibility and resolving conflicts",
            backstory="""You are an expert in Node.js package management and Angular ecosystem dependencies.
            You understand the intricate relationships between Angular packages, their peer dependencies,
            and how to resolve version conflicts. You specialize in updating package.json files,
            managing npm/yarn installations, and ensuring all dependencies work together harmoniously.""",
            tools=[self.file_read_tool, self.file_write_tool, self.directory_read_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Analyze current dependencies and identify update requirements"""
        package_json_path = os.path.join(project_path, "package.json")

        if not os.path.exists(package_json_path):
            return {"error": "package.json not found"}

        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            peer_dependencies = package_data.get('peerDependencies', {})

            analysis = {
                "current_angular_version": self._extract_angular_version(dependencies, dev_dependencies),
                "angular_packages": self._get_angular_packages(dependencies, dev_dependencies),
                "third_party_packages": self._get_third_party_packages(dependencies, dev_dependencies),
                "potential_conflicts": [],
                "update_recommendations": [],
                "compatibility_matrix": {}
            }

            # Check for potential conflicts
            analysis["potential_conflicts"] = self._check_dependency_conflicts(dependencies, dev_dependencies)

            # Generate update recommendations
            analysis["update_recommendations"] = self._generate_update_recommendations(
                analysis["angular_packages"],
                analysis["third_party_packages"]
            )

            return analysis

        except Exception as e:
            return {"error": f"Failed to analyze dependencies: {str(e)}"}

    def _extract_angular_version(self, dependencies: Dict, dev_dependencies: Dict) -> str:
        """Extract Angular core version"""
        angular_core = dependencies.get('@angular/core', dev_dependencies.get('@angular/core', ''))
        version_match = re.search(r'(\d+)', angular_core)
        return version_match.group(1) if version_match else "unknown"

    def _get_angular_packages(self, dependencies: Dict, dev_dependencies: Dict) -> Dict[str, str]:
        """Get all Angular packages and their versions"""
        angular_packages = {}

        for dep_dict in [dependencies, dev_dependencies]:
            for package, version in dep_dict.items():
                if package.startswith('@angular/'):
                    angular_packages[package] = version

        return angular_packages

    def _get_third_party_packages(self, dependencies: Dict, dev_dependencies: Dict) -> Dict[str, str]:
        """Get third-party packages that might need updates"""
        important_packages = [
            'rxjs', 'typescript', 'zone.js', 'tslib',
            '@angular-devkit/build-angular', 'karma', 'jasmine',
            'eslint', 'prettier', 'webpack'
        ]

        third_party = {}
        for dep_dict in [dependencies, dev_dependencies]:
            for package, version in dep_dict.items():
                if not package.startswith('@angular/') and (
                    package in important_packages or
                    'angular' in package.lower() or
                    package.startswith('@angular-')
                ):
                    third_party[package] = version

        return third_party

    def _check_dependency_conflicts(self, dependencies: Dict, dev_dependencies: Dict) -> List[Dict[str, Any]]:
        """Check for potential dependency conflicts"""
        conflicts = []

        # Check Angular version consistency
        angular_packages = self._get_angular_packages(dependencies, dev_dependencies)
        if angular_packages:
            versions = set()
            for package, version in angular_packages.items():
                version_clean = re.sub(r'[^\d.]', '', version.split('.')[0])
                if version_clean:
                    versions.add(version_clean)

            if len(versions) > 1:
                conflicts.append({
                    "type": "version_mismatch",
                    "description": "Angular packages have different major versions",
                    "packages": angular_packages,
                    "severity": "high"
                })

        # Check TypeScript compatibility
        typescript_version = dependencies.get('typescript', dev_dependencies.get('typescript', ''))
        if typescript_version:
            ts_major = re.search(r'(\d+)', typescript_version)
            if ts_major:
                ts_version = int(ts_major.group(1))
                angular_version = self._extract_angular_version(dependencies, dev_dependencies)

                if angular_version != "unknown":
                    expected_ts = self._get_typescript_compatibility(int(angular_version))
                    if ts_version not in expected_ts:
                        conflicts.append({
                            "type": "typescript_incompatibility",
                            "description": f"TypeScript {ts_version} may not be compatible with Angular {angular_version}",
                            "expected": expected_ts,
                            "current": ts_version,
                            "severity": "medium"
                        })

        return conflicts

    def _get_typescript_compatibility(self, angular_version: int) -> List[int]:
        """Get compatible TypeScript versions for Angular version"""
        compatibility_matrix = {
            17: [5, 6],
            18: [5, 6],
            19: [5, 6],
            20: [5, 6]
        }
        return compatibility_matrix.get(angular_version, [5])

    def _generate_update_recommendations(self, angular_packages: Dict, third_party_packages: Dict) -> List[Dict[str, Any]]:
        """Generate package update recommendations"""
        recommendations = []

        # Angular packages updates
        if angular_packages:
            current_version = None
            for package, version in angular_packages.items():
                if package == '@angular/core':
                    version_match = re.search(r'(\d+)', version)
                    current_version = int(version_match.group(1)) if version_match else None
                    break

            if current_version and current_version < 20:
                target_version = "20.3.0"
                recommendations.append({
                    "type": "major_update",
                    "description": f"Update Angular from {current_version} to 20",
                    "packages": list(angular_packages.keys()),
                    "target_version": target_version,
                    "command": f"ng update @angular/core @angular/cli --to={target_version}",
                    "priority": "high"
                })

        # Third-party package recommendations
        package_updates = {
            'typescript': {'version': '~5.8.3', 'reason': 'Angular 20 compatibility'},
            'rxjs': {'version': '~7.8.0', 'reason': 'Latest stable version'},
            'zone.js': {'version': '~0.15.1', 'reason': 'Angular 20 compatibility'},
            'eslint': {'version': '^9.35.0', 'reason': 'Latest ESLint version'},
            'prettier': {'version': '^3.6.2', 'reason': 'Code formatting updates'}
        }

        for package, info in package_updates.items():
            if package in third_party_packages:
                current = third_party_packages[package]
                if current != info['version']:
                    recommendations.append({
                        "type": "minor_update",
                        "description": f"Update {package} to {info['version']}",
                        "package": package,
                        "current_version": current,
                        "target_version": info['version'],
                        "reason": info['reason'],
                        "command": f"npm install {package}@{info['version']}",
                        "priority": "medium"
                    })

        return recommendations

    def create_migration_package_json(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Create updated package.json for target Angular version"""
        package_json_path = os.path.join(project_path, "package.json")

        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            # Update Angular packages
            angular_20_versions = {
                "@angular/animations": "^20.3.0",
                "@angular/common": "^20.3.0",
                "@angular/compiler": "^20.3.0",
                "@angular/core": "^20.3.0",
                "@angular/forms": "^20.3.0",
                "@angular/platform-browser": "^20.3.0",
                "@angular/platform-browser-dynamic": "^20.3.0",
                "@angular/platform-server": "^20.3.0",
                "@angular/router": "^20.3.0",
                "@angular/ssr": "^20.3.0"
            }

            angular_20_dev_versions = {
                "@angular-devkit/build-angular": "^20.3.0",
                "@angular/cli": "^20.3.0",
                "@angular/compiler-cli": "^20.3.0"
            }

            # Update dependencies
            for package, version in angular_20_versions.items():
                if package in package_data.get('dependencies', {}):
                    package_data['dependencies'][package] = version

            # Update dev dependencies
            for package, version in angular_20_dev_versions.items():
                if package in package_data.get('devDependencies', {}):
                    package_data['devDependencies'][package] = version

            # Update other important packages
            other_updates = {
                'dependencies': {
                    'rxjs': '~7.8.0',
                    'tslib': '^2.3.0',
                    'zone.js': '~0.15.1'
                },
                'devDependencies': {
                    'typescript': '~5.8.3',
                    '@types/jasmine': '~5.1.0',
                    '@types/node': '^18.18.0',
                    'jasmine-core': '~5.1.0',
                    'karma': '~6.4.0',
                    'karma-chrome-launcher': '~3.2.0',
                    'karma-coverage': '~2.2.0',
                    'karma-jasmine': '~5.1.0',
                    'karma-jasmine-html-reporter': '~2.1.0'
                }
            }

            for dep_type, updates in other_updates.items():
                if dep_type in package_data:
                    for package, version in updates.items():
                        if package in package_data[dep_type]:
                            package_data[dep_type][package] = version

            return {
                "success": True,
                "updated_package_json": package_data,
                "changes": self._get_package_changes(package_json_path, package_data)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_package_changes(self, original_path: str, new_data: Dict) -> List[Dict[str, Any]]:
        """Compare original and new package.json to show changes"""
        try:
            with open(original_path, 'r') as f:
                original_data = json.load(f)

            changes = []

            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in new_data:
                    for package, new_version in new_data[dep_type].items():
                        old_version = original_data.get(dep_type, {}).get(package)
                        if old_version and old_version != new_version:
                            changes.append({
                                "package": package,
                                "type": dep_type,
                                "old_version": old_version,
                                "new_version": new_version
                            })

            return changes
        except:
            return []

    def execute_dependency_update(self, project_path: str, update_command: str) -> Dict[str, Any]:
        """Execute dependency update command"""
        try:
            result = subprocess.run(
                update_command.split(),
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validate_dependencies(self, project_path: str) -> Dict[str, Any]:
        """Validate that all dependencies are properly installed and compatible"""
        try:
            # Check if node_modules exists
            node_modules_path = os.path.join(project_path, "node_modules")
            if not os.path.exists(node_modules_path):
                return {
                    "valid": False,
                    "error": "node_modules directory not found. Run npm install."
                }

            # Run npm ls to check for missing dependencies
            result = subprocess.run(
                ["npm", "ls", "--depth=0"],
                cwd=project_path,
                capture_output=True,
                text=True
            )

            issues = []
            if result.returncode != 0:
                # Parse npm ls output for specific issues
                if "missing" in result.stderr:
                    issues.append("Missing dependencies detected")
                if "peer dep missing" in result.stderr:
                    issues.append("Peer dependencies missing")

            return {
                "valid": result.returncode == 0,
                "issues": issues,
                "npm_ls_output": result.stdout,
                "npm_ls_errors": result.stderr
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to validate dependencies: {str(e)}"
            }