"""
Angular Migration Analyzer Agent
Analyzes Angular projects and determines migration requirements
"""

from crewai import Agent
from crewai_tools import FileReadTool, DirectoryReadTool, CodeDocsSearchTool
import json
import os
from typing import Dict, List, Any


class AngularMigrationAnalyzer:
    """Agent specialized in analyzing Angular projects for migration requirements"""

    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.directory_read_tool = DirectoryReadTool()
        self.code_search_tool = CodeDocsSearchTool()

    def create_agent(self) -> Agent:
        return Agent(
            role="Angular Migration Analyzer",
            goal="Analyze Angular projects to determine current version, dependencies, and migration requirements",
            backstory="""You are an expert Angular developer with deep knowledge of Angular's evolution
            from version 2 to 20+. You specialize in analyzing codebases to understand their current state
            and determining the optimal migration path. You can identify deprecated APIs, breaking changes,
            and compatibility issues across different Angular versions.""",
            tools=[self.file_read_tool, self.directory_read_tool, self.code_search_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze the project structure and return a comprehensive report"""
        analysis_result = {
            "current_version": None,
            "target_version": None,
            "package_json_analysis": {},
            "angular_json_analysis": {},
            "tsconfig_analysis": {},
            "dependencies": {},
            "dev_dependencies": {},
            "peer_dependencies": {},
            "deprecated_features": [],
            "breaking_changes": [],
            "migration_recommendations": []
        }

        # Analyze package.json
        package_json_path = os.path.join(project_path, "package.json")
        if os.path.exists(package_json_path):
            analysis_result["package_json_analysis"] = self._analyze_package_json(package_json_path)

        # Analyze angular.json
        angular_json_path = os.path.join(project_path, "angular.json")
        if os.path.exists(angular_json_path):
            analysis_result["angular_json_analysis"] = self._analyze_angular_json(angular_json_path)

        # Analyze tsconfig files
        analysis_result["tsconfig_analysis"] = self._analyze_tsconfig_files(project_path)

        # Analyze source code for deprecated features
        analysis_result["deprecated_features"] = self._scan_deprecated_features(project_path)

        return analysis_result

    def _analyze_package_json(self, package_json_path: str) -> Dict[str, Any]:
        """Analyze package.json for Angular version and dependencies"""
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})

            # Extract Angular version
            angular_core_version = dependencies.get('@angular/core',
                                                  dev_dependencies.get('@angular/core', 'unknown'))

            # Analyze all Angular packages
            angular_packages = {}
            for dep_type in ['dependencies', 'devDependencies']:
                for package, version in package_data.get(dep_type, {}).items():
                    if package.startswith('@angular/'):
                        angular_packages[package] = version

            return {
                "angular_core_version": angular_core_version,
                "angular_packages": angular_packages,
                "node_version": package_data.get('engines', {}).get('node'),
                "npm_version": package_data.get('engines', {}).get('npm'),
                "scripts": package_data.get('scripts', {}),
                "all_dependencies": len(dependencies),
                "all_dev_dependencies": len(dev_dependencies)
            }
        except Exception as e:
            return {"error": f"Failed to analyze package.json: {str(e)}"}

    def _analyze_angular_json(self, angular_json_path: str) -> Dict[str, Any]:
        """Analyze angular.json for project configuration"""
        try:
            with open(angular_json_path, 'r') as f:
                angular_data = json.load(f)

            version = angular_data.get('version', 'unknown')
            projects = angular_data.get('projects', {})

            project_analysis = {}
            for project_name, project_config in projects.items():
                project_analysis[project_name] = {
                    "project_type": project_config.get('projectType'),
                    "build_options": project_config.get('architect', {}).get('build', {}).get('options', {}),
                    "serve_options": project_config.get('architect', {}).get('serve', {}).get('options', {}),
                    "test_options": project_config.get('architect', {}).get('test', {}).get('options', {})
                }

            return {
                "angular_json_version": version,
                "projects": project_analysis,
                "default_project": angular_data.get('defaultProject'),
                "cli_config": angular_data.get('cli', {})
            }
        except Exception as e:
            return {"error": f"Failed to analyze angular.json: {str(e)}"}

    def _analyze_tsconfig_files(self, project_path: str) -> Dict[str, Any]:
        """Analyze TypeScript configuration files"""
        tsconfig_files = ['tsconfig.json', 'tsconfig.app.json', 'tsconfig.spec.json']
        analysis = {}

        for config_file in tsconfig_files:
            config_path = os.path.join(project_path, config_file)
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        # Simple JSON parsing (ignoring comments)
                        content = f.read()
                        # Remove comments for basic parsing
                        lines = content.split('\n')
                        clean_lines = [line for line in lines if not line.strip().startswith('//')]
                        clean_content = '\n'.join(clean_lines)

                        config_data = json.loads(clean_content)
                        analysis[config_file] = {
                            "target": config_data.get('compilerOptions', {}).get('target'),
                            "module": config_data.get('compilerOptions', {}).get('module'),
                            "lib": config_data.get('compilerOptions', {}).get('lib', []),
                            "strict": config_data.get('compilerOptions', {}).get('strict'),
                            "extends": config_data.get('extends')
                        }
                except Exception as e:
                    analysis[config_file] = {"error": f"Failed to parse: {str(e)}"}

        return analysis

    def _scan_deprecated_features(self, project_path: str) -> List[Dict[str, Any]]:
        """Scan source code for deprecated Angular features"""
        deprecated_patterns = [
            {"pattern": "HttpModule", "replacement": "HttpClientModule", "version": "4.3+"},
            {"pattern": "Http", "replacement": "HttpClient", "version": "4.3+"},
            {"pattern": "OpaqueToken", "replacement": "InjectionToken", "version": "4+"},
            {"pattern": "Renderer", "replacement": "Renderer2", "version": "4+"},
            {"pattern": "PLATFORM_DIRECTIVES", "replacement": "schemas in NgModule", "version": "2+"},
            {"pattern": "ComponentResolver", "replacement": "ComponentFactoryResolver", "version": "2+"},
            {"pattern": "RootRenderer", "replacement": "RendererFactory2", "version": "4+"},
            {"pattern": ".forRoot()", "note": "Check if still needed in newer versions", "version": "14+"},
            {"pattern": "ModuleWithProviders", "note": "Generic type required", "version": "9+"}
        ]

        deprecated_found = []
        src_path = os.path.join(project_path, "src")

        if os.path.exists(src_path):
            for root, dirs, files in os.walk(src_path):
                for file in files:
                    if file.endswith(('.ts', '.js', '.html')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for pattern_info in deprecated_patterns:
                                    if pattern_info["pattern"] in content:
                                        deprecated_found.append({
                                            "file": file_path,
                                            "pattern": pattern_info["pattern"],
                                            "replacement": pattern_info.get("replacement"),
                                            "note": pattern_info.get("note"),
                                            "version": pattern_info["version"]
                                        })
                        except Exception as e:
                            continue

        return deprecated_found

    def get_migration_roadmap(self, current_version: str, target_version: str) -> List[Dict[str, Any]]:
        """Generate a migration roadmap from current to target version"""
        version_map = {
            "17": ["18", "19", "20"],
            "18": ["19", "20"],
            "19": ["20"],
            "20": []
        }

        current_major = current_version.split('.')[0]
        target_major = target_version.split('.')[0]

        if current_major in version_map:
            migration_steps = []
            for step_version in version_map[current_major]:
                if int(step_version) <= int(target_major):
                    migration_steps.append({
                        "from_version": current_major if not migration_steps else migration_steps[-1]["to_version"],
                        "to_version": step_version,
                        "estimated_time": "2-4 hours",
                        "complexity": "Medium",
                        "breaking_changes": self._get_breaking_changes_for_version(step_version)
                    })
                    current_major = step_version

            return migration_steps

        return []

    def _get_breaking_changes_for_version(self, version: str) -> List[str]:
        """Get breaking changes for a specific Angular version"""
        breaking_changes = {
            "18": [
                "Material + CDK support for Angular 18",
                "Control flow syntax (@if, @for, @switch) becomes stable",
                "Angular Material 3 support",
                "Built-in control flow replaces *ngIf, *ngFor"
            ],
            "19": [
                "Standalone APIs become default",
                "New lifecycle hooks for SSR",
                "Hydration improvements",
                "Optional injectors in Embedded Views"
            ],
            "20": [
                "New Angular DevKit architecture",
                "Improved SSR and hydration",
                "Enhanced performance optimizations",
                "New build system improvements"
            ]
        }
        return breaking_changes.get(version, [])