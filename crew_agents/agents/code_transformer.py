"""
Code Transformer Agent
Handles code transformations, API migrations, and syntax updates
"""

from crewai import Agent
from crewai_tools import FileReadTool, FileWriteTool, DirectoryReadTool
import os
import re
from typing import Dict, List, Any, Tuple
import ast


class CodeTransformer:
    """Agent specialized in transforming Angular code during migration"""

    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.file_write_tool = FileWriteTool()
        self.directory_read_tool = DirectoryReadTool()

    def create_agent(self) -> Agent:
        return Agent(
            role="Angular Code Transformer",
            goal="Transform Angular code to use new APIs, syntax, and patterns during migration",
            backstory="""You are an expert Angular developer who specializes in code transformations
            and migrations. You understand the evolution of Angular APIs, syntax changes, and
            best practices across different versions. You can automatically refactor code to use
            new patterns, update deprecated APIs, and ensure code follows modern Angular conventions.""",
            tools=[self.file_read_tool, self.file_write_tool, self.directory_read_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyze_code_changes_needed(self, project_path: str, target_version: str) -> Dict[str, Any]:
        """Analyze code and identify transformations needed for target version"""
        src_path = os.path.join(project_path, "src")
        analysis_result = {
            "files_to_transform": [],
            "transformations_needed": [],
            "deprecated_apis": [],
            "new_features_to_adopt": [],
            "estimated_effort": "low"
        }

        if not os.path.exists(src_path):
            return {"error": "src directory not found"}

        # Scan TypeScript files
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith('.ts'):
                    file_path = os.path.join(root, file)
                    file_analysis = self._analyze_typescript_file(file_path, target_version)
                    if file_analysis["needs_transformation"]:
                        analysis_result["files_to_transform"].append({
                            "file": file_path,
                            "transformations": file_analysis["transformations"]
                        })

        # Scan HTML templates
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    template_analysis = self._analyze_template_file(file_path, target_version)
                    if template_analysis["needs_transformation"]:
                        analysis_result["files_to_transform"].append({
                            "file": file_path,
                            "transformations": template_analysis["transformations"]
                        })

        # Calculate estimated effort
        total_transformations = sum(len(f["transformations"]) for f in analysis_result["files_to_transform"])
        if total_transformations > 50:
            analysis_result["estimated_effort"] = "high"
        elif total_transformations > 20:
            analysis_result["estimated_effort"] = "medium"

        return analysis_result

    def _analyze_typescript_file(self, file_path: str, target_version: str) -> Dict[str, Any]:
        """Analyze TypeScript file for needed transformations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            transformations = []

            # Check for deprecated imports
            deprecated_imports = self._check_deprecated_imports(content)
            transformations.extend(deprecated_imports)

            # Check for deprecated APIs
            deprecated_apis = self._check_deprecated_apis(content)
            transformations.extend(deprecated_apis)

            # Check for Angular 18+ control flow syntax opportunities
            if int(target_version.split('.')[0]) >= 18:
                control_flow_transforms = self._check_control_flow_transforms(content)
                transformations.extend(control_flow_transforms)

            # Check for standalone component opportunities
            if int(target_version.split('.')[0]) >= 14:
                standalone_transforms = self._check_standalone_transforms(content)
                transformations.extend(standalone_transforms)

            return {
                "needs_transformation": len(transformations) > 0,
                "transformations": transformations
            }

        except Exception as e:
            return {
                "needs_transformation": False,
                "error": f"Failed to analyze {file_path}: {str(e)}"
            }

    def _analyze_template_file(self, file_path: str, target_version: str) -> Dict[str, Any]:
        """Analyze HTML template file for needed transformations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            transformations = []

            # Check for Angular 18+ control flow syntax opportunities
            if int(target_version.split('.')[0]) >= 18:
                template_transforms = self._check_template_control_flow(content)
                transformations.extend(template_transforms)

            # Check for deprecated template syntax
            deprecated_template = self._check_deprecated_template_syntax(content)
            transformations.extend(deprecated_template)

            return {
                "needs_transformation": len(transformations) > 0,
                "transformations": transformations
            }

        except Exception as e:
            return {
                "needs_transformation": False,
                "error": f"Failed to analyze template {file_path}: {str(e)}"
            }

    def _check_deprecated_imports(self, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated import statements"""
        transformations = []

        deprecated_import_patterns = [
            {
                "pattern": r"import\s*\{\s*HttpModule\s*\}\s*from\s*['\"]@angular/http['\"]",
                "replacement": "import { HttpClientModule } from '@angular/common/http'",
                "description": "Replace HttpModule with HttpClientModule"
            },
            {
                "pattern": r"import\s*\{\s*Http\s*\}\s*from\s*['\"]@angular/http['\"]",
                "replacement": "import { HttpClient } from '@angular/common/http'",
                "description": "Replace Http with HttpClient"
            },
            {
                "pattern": r"import\s*\{\s*Renderer\s*\}\s*from\s*['\"]@angular/core['\"]",
                "replacement": "import { Renderer2 } from '@angular/core'",
                "description": "Replace Renderer with Renderer2"
            }
        ]

        for pattern_info in deprecated_import_patterns:
            matches = re.finditer(pattern_info["pattern"], content)
            for match in matches:
                transformations.append({
                    "type": "import_replacement",
                    "description": pattern_info["description"],
                    "line_content": match.group(0),
                    "replacement": pattern_info["replacement"],
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return transformations

    def _check_deprecated_apis(self, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated API usage"""
        transformations = []

        deprecated_api_patterns = [
            {
                "pattern": r"\.subscribe\(\s*\w+\s*=>\s*\{[^}]*\},\s*\w+\s*=>\s*\{[^}]*\}\s*\)",
                "description": "Consider using async pipe or modern RxJS operators",
                "suggestion": "Use async pipe in template or modern error handling"
            },
            {
                "pattern": r"ElementRef\.nativeElement\.innerHTML\s*=",
                "description": "Direct DOM manipulation should use Renderer2",
                "suggestion": "Use Renderer2.setProperty or Renderer2.setAttribute"
            },
            {
                "pattern": r"ViewChild\(['\"][^'\"]+['\"]\)",
                "description": "String-based ViewChild selectors deprecated",
                "suggestion": "Use template reference variables or component types"
            }
        ]

        for pattern_info in deprecated_api_patterns:
            matches = re.finditer(pattern_info["pattern"], content)
            for match in matches:
                transformations.append({
                    "type": "api_deprecation",
                    "description": pattern_info["description"],
                    "line_content": match.group(0),
                    "suggestion": pattern_info["suggestion"],
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return transformations

    def _check_control_flow_transforms(self, content: str) -> List[Dict[str, Any]]:
        """Check for opportunities to use Angular 18+ control flow syntax"""
        transformations = []

        # This would be used in templates, but we can check component logic
        control_flow_patterns = [
            {
                "pattern": r"showElement\s*=\s*[^;]+;",
                "description": "Consider using @if in template for conditional rendering",
                "suggestion": "Use @if directive in template instead of component property"
            }
        ]

        for pattern_info in control_flow_patterns:
            matches = re.finditer(pattern_info["pattern"], content)
            for match in matches:
                transformations.append({
                    "type": "control_flow_suggestion",
                    "description": pattern_info["description"],
                    "line_content": match.group(0),
                    "suggestion": pattern_info["suggestion"],
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return transformations

    def _check_standalone_transforms(self, content: str) -> List[Dict[str, Any]]:
        """Check for opportunities to convert to standalone components"""
        transformations = []

        # Check if component is already standalone
        if "standalone: true" in content:
            return transformations

        # Check for component decorator
        component_match = re.search(r"@Component\s*\(\s*\{([^}]+)\}\s*\)", content, re.DOTALL)
        if component_match:
            component_config = component_match.group(1)

            # Check if it imports modules (candidate for standalone conversion)
            if "imports:" not in component_config and "@NgModule" not in content:
                transformations.append({
                    "type": "standalone_conversion",
                    "description": "Component can be converted to standalone",
                    "suggestion": "Add 'standalone: true' and specify imports directly",
                    "start_pos": component_match.start(),
                    "end_pos": component_match.end()
                })

        return transformations

    def _check_template_control_flow(self, content: str) -> List[Dict[str, Any]]:
        """Check template for Angular 18+ control flow opportunities"""
        transformations = []

        control_flow_patterns = [
            {
                "pattern": r"\*ngIf=\"([^\"]+)\"",
                "replacement": "@if (\\1) {",
                "description": "Convert *ngIf to @if control flow"
            },
            {
                "pattern": r"\*ngFor=\"let\s+(\w+)\s+of\s+([^;\"]+)\"",
                "replacement": "@for (\\1 of \\2; track \\1) {",
                "description": "Convert *ngFor to @for control flow"
            },
            {
                "pattern": r"\[ngSwitch\]=\"([^\"]+)\"",
                "replacement": "@switch (\\1) {",
                "description": "Convert ngSwitch to @switch control flow"
            }
        ]

        for pattern_info in control_flow_patterns:
            matches = re.finditer(pattern_info["pattern"], content)
            for match in matches:
                transformations.append({
                    "type": "template_control_flow",
                    "description": pattern_info["description"],
                    "line_content": match.group(0),
                    "replacement": re.sub(pattern_info["pattern"], pattern_info["replacement"], match.group(0)),
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return transformations

    def _check_deprecated_template_syntax(self, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated template syntax"""
        transformations = []

        deprecated_patterns = [
            {
                "pattern": r"\(\w+\)=\"\w+\(\$event\)\"",
                "description": "Consider using Angular event binding best practices",
                "suggestion": "Use proper event handler methods"
            }
        ]

        for pattern_info in deprecated_patterns:
            matches = re.finditer(pattern_info["pattern"], content)
            for match in matches:
                transformations.append({
                    "type": "template_deprecation",
                    "description": pattern_info["description"],
                    "line_content": match.group(0),
                    "suggestion": pattern_info["suggestion"],
                    "start_pos": match.start(),
                    "end_pos": match.end()
                })

        return transformations

    def apply_transformations(self, file_path: str, transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply transformations to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            modified_content = original_content
            applied_transformations = []

            # Sort transformations by position (reverse order to maintain positions)
            transformations.sort(key=lambda x: x.get('start_pos', 0), reverse=True)

            for transformation in transformations:
                if transformation["type"] in ["import_replacement", "template_control_flow"]:
                    if "replacement" in transformation:
                        start_pos = transformation["start_pos"]
                        end_pos = transformation["end_pos"]

                        modified_content = (
                            modified_content[:start_pos] +
                            transformation["replacement"] +
                            modified_content[end_pos:]
                        )

                        applied_transformations.append(transformation)

            # Write back the modified content
            if modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)

                return {
                    "success": True,
                    "applied_transformations": applied_transformations,
                    "changes_made": len(applied_transformations)
                }
            else:
                return {
                    "success": True,
                    "applied_transformations": [],
                    "changes_made": 0,
                    "message": "No changes were applied"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to apply transformations to {file_path}: {str(e)}"
            }

    def convert_to_standalone_component(self, component_file: str) -> Dict[str, Any]:
        """Convert a component to standalone"""
        try:
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the @Component decorator
            component_match = re.search(r"(@Component\s*\(\s*\{)([^}]+)(\}\s*\))", content, re.DOTALL)
            if not component_match:
                return {"success": False, "error": "No @Component decorator found"}

            decorator_start = component_match.group(1)
            decorator_content = component_match.group(2)
            decorator_end = component_match.group(3)

            # Check if already standalone
            if "standalone:" in decorator_content:
                return {"success": False, "error": "Component is already standalone"}

            # Add standalone: true and common imports
            new_decorator_content = decorator_content.rstrip()
            if not new_decorator_content.endswith(','):
                new_decorator_content += ','

            new_decorator_content += """
  standalone: true,
  imports: [CommonModule, FormsModule]"""

            new_component_decorator = decorator_start + new_decorator_content + decorator_end

            # Replace the old decorator
            new_content = content.replace(component_match.group(0), new_component_decorator)

            # Add necessary imports at the top
            import_additions = [
                "import { CommonModule } from '@angular/common';",
                "import { FormsModule } from '@angular/forms';"
            ]

            # Find the last import and add our imports
            import_matches = list(re.finditer(r"import\s+.*?;", new_content))
            if import_matches:
                last_import = import_matches[-1]
                insertion_point = last_import.end()

                for import_line in import_additions:
                    if import_line not in new_content:
                        new_content = (
                            new_content[:insertion_point] +
                            "\n" + import_line +
                            new_content[insertion_point:]
                        )
                        insertion_point += len(import_line) + 1

            # Write the modified content back
            with open(component_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return {
                "success": True,
                "message": "Component converted to standalone successfully",
                "changes": [
                    "Added standalone: true",
                    "Added CommonModule and FormsModule imports",
                    "Updated component decorator"
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to convert component to standalone: {str(e)}"
            }

    def migrate_control_flow_syntax(self, template_file: str) -> Dict[str, Any]:
        """Migrate template to use Angular 18+ control flow syntax"""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            transformations_applied = []

            # Convert *ngIf to @if
            ngif_pattern = r'<([^>]*)\*ngIf="([^"]+)"([^>]*)>(.*?)</\1>'
            def replace_ngif(match):
                tag = match.group(1)
                condition = match.group(2)
                attributes = match.group(3)
                inner_content = match.group(4)
                transformations_applied.append(f"Converted *ngIf=\"{condition}\" to @if")
                return f"@if ({condition}) {{\n  <{tag}{attributes}>{inner_content}</{tag}>\n}}"

            content = re.sub(ngif_pattern, replace_ngif, content, flags=re.DOTALL)

            # Convert *ngFor to @for
            ngfor_pattern = r'<([^>]*)\*ngFor="let\s+(\w+)\s+of\s+([^;"]+)"([^>]*)>(.*?)</\1>'
            def replace_ngfor(match):
                tag = match.group(1)
                item = match.group(2)
                collection = match.group(3)
                attributes = match.group(4)
                inner_content = match.group(5)
                transformations_applied.append(f"Converted *ngFor to @for with {item} of {collection}")
                return f"@for ({item} of {collection}; track {item}) {{\n  <{tag}{attributes}>{inner_content}</{tag}>\n}}"

            content = re.sub(ngfor_pattern, replace_ngfor, content, flags=re.DOTALL)

            if content != original_content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                return {
                    "success": True,
                    "transformations_applied": transformations_applied,
                    "message": f"Applied {len(transformations_applied)} control flow transformations"
                }
            else:
                return {
                    "success": True,
                    "transformations_applied": [],
                    "message": "No control flow transformations needed"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to migrate control flow syntax: {str(e)}"
            }