"""
Angular CLI MCP (Model Context Protocol) Server
Provides Angular CLI integration for CrewAI agents
"""

import json
import subprocess
import os
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime


class AngularCLIMCP:
    """MCP server for Angular CLI operations"""

    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.tools = {
            "ng_version": self._ng_version,
            "ng_update": self._ng_update,
            "ng_build": self._ng_build,
            "ng_test": self._ng_test,
            "ng_lint": self._ng_lint,
            "ng_generate": self._ng_generate,
            "ng_add": self._ng_add,
            "ng_serve": self._ng_serve,
            "ng_analytics": self._ng_analytics,
            "ng_config": self._ng_config
        }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific Angular CLI tool"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }

        try:
            return await self.tools[tool_name](**arguments)
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}"
            }

    async def _ng_version(self, **kwargs) -> Dict[str, Any]:
        """Get Angular CLI and project version information"""
        try:
            result = subprocess.run(
                ["ng", "version"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            version_info = self._parse_ng_version_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "version_info": version_info,
                "raw_output": result.stdout,
                "errors": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng version command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_update(self, packages: List[str] = None, to_version: str = None, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Update Angular packages"""
        try:
            cmd = ["ng", "update"]

            if packages:
                cmd.extend(packages)
            else:
                cmd.append("@angular/core")
                cmd.append("@angular/cli")

            if to_version:
                cmd.extend(["--to", to_version])

            if force:
                cmd.append("--force")

            # Add other common flags
            cmd.append("--allow-dirty")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for updates
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode,
                "migration_info": self._parse_update_output(result.stdout)
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng update command timed out after 10 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_build(self, configuration: str = "production", output_path: str = None, **kwargs) -> Dict[str, Any]:
        """Build the Angular application"""
        try:
            cmd = ["ng", "build"]

            if configuration:
                cmd.extend(["--configuration", configuration])

            if output_path:
                cmd.extend(["--output-path", output_path])

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            build_info = self._parse_build_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "build_info": build_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng build command timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_test(self, watch: bool = False, browsers: str = "ChromeHeadless", code_coverage: bool = False, **kwargs) -> Dict[str, Any]:
        """Run unit tests"""
        try:
            cmd = ["ng", "test"]

            if not watch:
                cmd.append("--watch=false")

            if browsers:
                cmd.extend(["--browsers", browsers])

            if code_coverage:
                cmd.append("--code-coverage")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            test_results = self._parse_test_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "test_results": test_results,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng test command timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_lint(self, fix: bool = False, **kwargs) -> Dict[str, Any]:
        """Run linting"""
        try:
            cmd = ["ng", "lint"]

            if fix:
                cmd.append("--fix")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            lint_results = self._parse_lint_output(result.stdout + result.stderr)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "lint_results": lint_results,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng lint command timed out after 2 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_generate(self, schematic: str, name: str, options: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate Angular schematics"""
        try:
            cmd = ["ng", "generate", schematic, name]

            if options:
                for key, value in options.items():
                    if isinstance(value, bool):
                        if value:
                            cmd.append(f"--{key}")
                    else:
                        cmd.extend([f"--{key}", str(value)])

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            generated_files = self._parse_generate_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "generated_files": generated_files,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng generate command timed out after 1 minute"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_add(self, package: str, **kwargs) -> Dict[str, Any]:
        """Add a package using ng add"""
        try:
            cmd = ["ng", "add", package]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ng add command timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_serve(self, port: int = 4200, host: str = "localhost", open_browser: bool = False, **kwargs) -> Dict[str, Any]:
        """Start development server (non-blocking)"""
        try:
            cmd = ["ng", "serve", "--port", str(port), "--host", host]

            if open_browser:
                cmd.append("--open")

            # Start the server in the background
            process = subprocess.Popen(
                cmd,
                cwd=self.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a bit to see if it starts successfully
            await asyncio.sleep(5)

            if process.poll() is None:
                return {
                    "success": True,
                    "message": f"Development server started on http://{host}:{port}",
                    "pid": process.pid,
                    "command": " ".join(cmd)
                }
            else:
                stdout, stderr = process.communicate()
                return {
                    "success": False,
                    "error": "Failed to start development server",
                    "output": stdout,
                    "errors": stderr
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_analytics(self, enable: bool = None, **kwargs) -> Dict[str, Any]:
        """Manage Angular CLI analytics"""
        try:
            if enable is None:
                cmd = ["ng", "analytics"]
            else:
                cmd = ["ng", "analytics", "on" if enable else "off"]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _ng_config(self, json_path: str = None, value: Any = None, **kwargs) -> Dict[str, Any]:
        """Get or set Angular CLI configuration"""
        try:
            cmd = ["ng", "config"]

            if json_path:
                cmd.append(json_path)

            if value is not None:
                cmd.append(str(value))

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout.strip(),
                "errors": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_ng_version_output(self, output: str) -> Dict[str, str]:
        """Parse ng version output"""
        version_info = {}
        lines = output.split('\n')

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                version_info[key.strip()] = value.strip()

        return version_info

    def _parse_update_output(self, output: str) -> Dict[str, Any]:
        """Parse ng update output"""
        migration_info = {
            "migrations_run": [],
            "packages_updated": [],
            "warnings": [],
            "errors": []
        }

        lines = output.split('\n')
        for line in lines:
            if "Executing migration" in line:
                migration_info["migrations_run"].append(line.strip())
            elif "UPDATE" in line and "package.json" in line:
                migration_info["packages_updated"].append(line.strip())
            elif "WARNING" in line:
                migration_info["warnings"].append(line.strip())
            elif "ERROR" in line:
                migration_info["errors"].append(line.strip())

        return migration_info

    def _parse_build_output(self, output: str) -> Dict[str, Any]:
        """Parse ng build output"""
        build_info = {
            "chunks": [],
            "warnings": [],
            "errors": [],
            "build_time": None
        }

        lines = output.split('\n')
        for line in lines:
            if "chunk" in line.lower() and ("js" in line or "css" in line):
                build_info["chunks"].append(line.strip())
            elif "warning" in line.lower():
                build_info["warnings"].append(line.strip())
            elif "error" in line.lower():
                build_info["errors"].append(line.strip())
            elif "built at:" in line.lower():
                build_info["build_time"] = line.strip()

        return build_info

    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse ng test output"""
        test_info = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": None
        }

        # Parse test results
        if "tests completed" in output:
            import re
            match = re.search(r'(\d+) tests completed', output)
            if match:
                test_info["total"] = int(match.group(1))

        return test_info

    def _parse_lint_output(self, output: str) -> Dict[str, Any]:
        """Parse ng lint output"""
        lint_info = {
            "issues": [],
            "error_count": 0,
            "warning_count": 0
        }

        lines = output.split('\n')
        for line in lines:
            if " error " in line or " warning " in line:
                lint_info["issues"].append(line.strip())
                if " error " in line:
                    lint_info["error_count"] += 1
                else:
                    lint_info["warning_count"] += 1

        return lint_info

    def _parse_generate_output(self, output: str) -> List[str]:
        """Parse ng generate output"""
        generated_files = []
        lines = output.split('\n')

        for line in lines:
            if "CREATE" in line or "UPDATE" in line:
                parts = line.split()
                if len(parts) > 1:
                    generated_files.append(parts[-1])

        return generated_files

    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools and their descriptions"""
        return {
            "ng_version": "Get Angular CLI and project version information",
            "ng_update": "Update Angular packages",
            "ng_build": "Build the Angular application",
            "ng_test": "Run unit tests",
            "ng_lint": "Run linting",
            "ng_generate": "Generate Angular schematics (components, services, etc.)",
            "ng_add": "Add a package using ng add",
            "ng_serve": "Start development server",
            "ng_analytics": "Manage Angular CLI analytics",
            "ng_config": "Get or set Angular CLI configuration"
        }