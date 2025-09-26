"""
NPM MCP (Model Context Protocol) Server
Provides npm package management integration for CrewAI agents
"""

import json
import subprocess
import os
from typing import Dict, List, Any, Optional
import asyncio
import re


class NPMMCP:
    """MCP server for NPM operations"""

    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.tools = {
            "npm_install": self._npm_install,
            "npm_update": self._npm_update,
            "npm_uninstall": self._npm_uninstall,
            "npm_audit": self._npm_audit,
            "npm_list": self._npm_list,
            "npm_outdated": self._npm_outdated,
            "npm_run": self._npm_run,
            "npm_info": self._npm_info,
            "npm_search": self._npm_search,
            "npm_version": self._npm_version,
            "package_json_info": self._package_json_info
        }

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific NPM tool"""
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

    async def _npm_install(self, packages: List[str] = None, save_dev: bool = False,
                          save_exact: bool = False, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Install npm packages"""
        try:
            cmd = ["npm", "install"]

            if packages:
                cmd.extend(packages)

            if save_dev:
                cmd.append("--save-dev")

            if save_exact:
                cmd.append("--save-exact")

            if force:
                cmd.append("--force")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            install_info = self._parse_install_output(result.stdout + result.stderr)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "install_info": install_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm install command timed out after 10 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_update(self, packages: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Update npm packages"""
        try:
            cmd = ["npm", "update"]

            if packages:
                cmd.extend(packages)

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm update command timed out after 10 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_uninstall(self, packages: List[str], save: bool = True, **kwargs) -> Dict[str, Any]:
        """Uninstall npm packages"""
        try:
            cmd = ["npm", "uninstall"]
            cmd.extend(packages)

            if save:
                cmd.append("--save")

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
            return {"success": False, "error": "npm uninstall command timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_audit(self, fix: bool = False, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Run npm audit to check for vulnerabilities"""
        try:
            cmd = ["npm", "audit"]

            if fix:
                cmd.append("--fix")

            if force:
                cmd.append("--force")

            # Always add --json for better parsing
            if not fix:
                cmd.append("--json")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            audit_info = self._parse_audit_output(result.stdout, is_json=not fix)

            return {
                "success": result.returncode == 0 or result.returncode == 1,  # 1 means vulnerabilities found
                "command": " ".join(cmd),
                "audit_info": audit_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm audit command timed out after 5 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_list(self, depth: int = 0, production: bool = False, **kwargs) -> Dict[str, Any]:
        """List installed packages"""
        try:
            cmd = ["npm", "list", "--json"]

            if depth is not None:
                cmd.extend(["--depth", str(depth)])

            if production:
                cmd.append("--production")

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            list_info = self._parse_list_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "list_info": list_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm list command timed out after 1 minute"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_outdated(self, **kwargs) -> Dict[str, Any]:
        """Check for outdated packages"""
        try:
            cmd = ["npm", "outdated", "--json"]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            outdated_info = self._parse_outdated_output(result.stdout)

            return {
                "success": True,  # npm outdated returns non-zero when packages are outdated
                "command": " ".join(cmd),
                "outdated_info": outdated_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm outdated command timed out after 2 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_run(self, script: str, **kwargs) -> Dict[str, Any]:
        """Run npm script"""
        try:
            cmd = ["npm", "run", script]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for scripts
            )

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"npm run {script} command timed out after 10 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_info(self, package: str, **kwargs) -> Dict[str, Any]:
        """Get information about a package"""
        try:
            cmd = ["npm", "info", package, "--json"]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            package_info = self._parse_info_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "package_info": package_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm info command timed out after 1 minute"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search for packages"""
        try:
            cmd = ["npm", "search", query, "--json"]

            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            search_results = self._parse_search_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": " ".join(cmd),
                "search_results": search_results,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm search command timed out after 2 minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _npm_version(self, **kwargs) -> Dict[str, Any]:
        """Get npm and node version information"""
        try:
            result = subprocess.run(
                ["npm", "version", "--json"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            version_info = self._parse_version_output(result.stdout)

            return {
                "success": result.returncode == 0,
                "command": "npm version --json",
                "version_info": version_info,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "npm version command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _package_json_info(self, **kwargs) -> Dict[str, Any]:
        """Get package.json information"""
        try:
            package_json_path = os.path.join(self.project_path, "package.json")

            if not os.path.exists(package_json_path):
                return {
                    "success": False,
                    "error": "package.json not found in project directory"
                }

            with open(package_json_path, 'r') as f:
                package_data = json.load(f)

            analysis = {
                "name": package_data.get("name"),
                "version": package_data.get("version"),
                "description": package_data.get("description"),
                "main": package_data.get("main"),
                "scripts": package_data.get("scripts", {}),
                "dependencies": package_data.get("dependencies", {}),
                "devDependencies": package_data.get("devDependencies", {}),
                "peerDependencies": package_data.get("peerDependencies", {}),
                "engines": package_data.get("engines", {}),
                "repository": package_data.get("repository"),
                "author": package_data.get("author"),
                "license": package_data.get("license"),
                "keywords": package_data.get("keywords", []),
                "total_dependencies": len(package_data.get("dependencies", {})),
                "total_dev_dependencies": len(package_data.get("devDependencies", {})),
                "total_scripts": len(package_data.get("scripts", {}))
            }

            return {
                "success": True,
                "package_info": analysis,
                "raw_package_json": package_data
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in package.json: {str(e)}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_install_output(self, output: str) -> Dict[str, Any]:
        """Parse npm install output"""
        install_info = {
            "packages_added": [],
            "packages_updated": [],
            "vulnerabilities": 0,
            "warnings": []
        }

        lines = output.split('\n')
        for line in lines:
            if "added" in line and "package" in line:
                match = re.search(r'added (\d+) package', line)
                if match:
                    install_info["packages_added"] = int(match.group(1))
            elif "updated" in line and "package" in line:
                match = re.search(r'updated (\d+) package', line)
                if match:
                    install_info["packages_updated"] = int(match.group(1))
            elif "vulnerabilities" in line:
                match = re.search(r'(\d+) vulnerabilities', line)
                if match:
                    install_info["vulnerabilities"] = int(match.group(1))
            elif "WARN" in line:
                install_info["warnings"].append(line.strip())

        return install_info

    def _parse_audit_output(self, output: str, is_json: bool = True) -> Dict[str, Any]:
        """Parse npm audit output"""
        if is_json and output.strip():
            try:
                audit_data = json.loads(output)
                return {
                    "vulnerabilities": audit_data.get("vulnerabilities", {}),
                    "metadata": audit_data.get("metadata", {}),
                    "summary": audit_data.get("metadata", {}).get("vulnerabilities", {})
                }
            except json.JSONDecodeError:
                pass

        # Fallback to text parsing
        audit_info = {
            "vulnerabilities": {},
            "summary": {"total": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
        }

        lines = output.split('\n')
        for line in lines:
            if "vulnerabilities" in line.lower():
                # Parse vulnerability counts
                for severity in ["low", "moderate", "high", "critical"]:
                    match = re.search(f'(\\d+) {severity}', line, re.IGNORECASE)
                    if match:
                        audit_info["summary"][severity] = int(match.group(1))

        return audit_info

    def _parse_list_output(self, output: str) -> Dict[str, Any]:
        """Parse npm list output"""
        try:
            if output.strip():
                list_data = json.loads(output)
                return {
                    "name": list_data.get("name"),
                    "version": list_data.get("version"),
                    "dependencies": list_data.get("dependencies", {}),
                    "problems": list_data.get("problems", [])
                }
        except json.JSONDecodeError:
            pass

        return {"error": "Could not parse npm list output"}

    def _parse_outdated_output(self, output: str) -> Dict[str, Any]:
        """Parse npm outdated output"""
        try:
            if output.strip():
                outdated_data = json.loads(output)
                return {
                    "outdated_packages": outdated_data,
                    "count": len(outdated_data)
                }
        except json.JSONDecodeError:
            pass

        return {"outdated_packages": {}, "count": 0}

    def _parse_info_output(self, output: str) -> Dict[str, Any]:
        """Parse npm info output"""
        try:
            if output.strip():
                info_data = json.loads(output)
                return {
                    "name": info_data.get("name"),
                    "version": info_data.get("version"),
                    "description": info_data.get("description"),
                    "keywords": info_data.get("keywords", []),
                    "license": info_data.get("license"),
                    "repository": info_data.get("repository"),
                    "dependencies": info_data.get("dependencies", {}),
                    "devDependencies": info_data.get("devDependencies", {}),
                    "dist": info_data.get("dist", {}),
                    "maintainers": info_data.get("maintainers", [])
                }
        except json.JSONDecodeError:
            pass

        return {"error": "Could not parse npm info output"}

    def _parse_search_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse npm search output"""
        try:
            if output.strip():
                search_data = json.loads(output)
                return search_data[:10]  # Limit to first 10 results
        except json.JSONDecodeError:
            pass

        return []

    def _parse_version_output(self, output: str) -> Dict[str, Any]:
        """Parse npm version output"""
        try:
            if output.strip():
                version_data = json.loads(output)
                return version_data
        except json.JSONDecodeError:
            pass

        return {"error": "Could not parse npm version output"}

    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools and their descriptions"""
        return {
            "npm_install": "Install npm packages",
            "npm_update": "Update npm packages",
            "npm_uninstall": "Uninstall npm packages",
            "npm_audit": "Run security audit",
            "npm_list": "List installed packages",
            "npm_outdated": "Check for outdated packages",
            "npm_run": "Run npm scripts",
            "npm_info": "Get package information",
            "npm_search": "Search for packages",
            "npm_version": "Get npm and node version",
            "package_json_info": "Analyze package.json file"
        }