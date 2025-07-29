"""
Universal API Integration Engine - Auto-integrates with any digital service

This module enables NOVA to:
- Read OpenAPI/Swagger documentation and auto-generate integrations
- Dynamically create agent wrappers for any app/service
- Control any digital tool through natural language commands
- Build a unified interface for all user's digital tools
"""

import asyncio
import logging
import json
import yaml
import aiohttp
import ast
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import inspect

# Import core NOVA components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import BaseAgent, AgentType, Task, AgentCapability


@dataclass
class APIEndpoint:
    """Represents an API endpoint with its capabilities"""
    endpoint_id: str
    url: str
    method: str
    parameters: Dict[str, Any]
    description: str
    response_schema: Dict[str, Any]
    authentication: Dict[str, Any]
    rate_limits: Optional[Dict[str, Any]] = None


@dataclass
class ServiceIntegration:
    """Represents a complete service integration"""
    service_id: str
    service_name: str
    base_url: str
    api_version: str
    endpoints: List[APIEndpoint]
    authentication_config: Dict[str, Any]
    capabilities: List[str]
    generated_agent_code: str
    created_at: datetime


class UniversalAPIEngine:
    """Engine for automatic API integration and service control"""
    
    def __init__(self):
        self.logger = logging.getLogger("nova.api_engine")
        
        # Storage for integrations
        self.integrations: Dict[str, ServiceIntegration] = {}
        self.generated_agents: Dict[str, BaseAgent] = {}
        
        # API documentation cache
        self.api_docs_cache: Dict[str, Dict[str, Any]] = {}
        
        # Code generation templates
        self.agent_template = self._load_agent_template()
        
        # Initialize storage
        self.integrations_dir = Path("integrations/auto_generated")
        self.integrations_dir.mkdir(parents=True, exist_ok=True)
    
    async def integrate_service(self, service_identifier: str, auth_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Automatically integrate with any service using its API documentation"""
        try:
            self.logger.info(f"🔌 Starting auto-integration with {service_identifier}")
            
            # Step 1: Discover API documentation
            api_docs = await self._discover_api_documentation(service_identifier)
            
            if not api_docs:
                return {"success": False, "error": "Could not discover API documentation"}
            
            # Step 2: Parse API specification
            parsed_spec = await self._parse_api_specification(api_docs)
            
            # Step 3: Generate service integration
            integration = await self._generate_service_integration(service_identifier, parsed_spec, auth_config)
            
            # Step 4: Create agent wrapper
            agent = await self._generate_agent_wrapper(integration)
            
            # Step 5: Register integration
            self.integrations[service_identifier] = integration
            self.generated_agents[service_identifier] = agent
            
            # Step 6: Save generated code
            await self._save_integration(integration)
            
            return {
                "success": True,
                "service_id": service_identifier,
                "capabilities": integration.capabilities,
                "endpoints_count": len(integration.endpoints),
                "agent_generated": True,
                "message": f"Successfully integrated with {integration.service_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to integrate with {service_identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _discover_api_documentation(self, service_identifier: str) -> Optional[Dict[str, Any]]:
        """Discover API documentation for a service"""
        # Try multiple discovery methods
        
        # Method 1: Direct URL to OpenAPI/Swagger spec
        if service_identifier.startswith("http"):
            return await self._fetch_openapi_spec(service_identifier)
        
        # Method 2: Common API doc endpoints
        common_endpoints = [
            f"https://api.{service_identifier}.com/swagger.json",
            f"https://api.{service_identifier}.com/v1/swagger.json",
            f"https://api.{service_identifier}.com/openapi.json",
            f"https://{service_identifier}.com/api/docs/swagger.json",
            f"https://{service_identifier}.com/.well-known/openapi.json"
        ]
        
        for endpoint in common_endpoints:
            try:
                spec = await self._fetch_openapi_spec(endpoint)
                if spec:
                    return spec
            except:
                continue
        
        # Method 3: Search for public API specifications
        return await self._search_public_api_specs(service_identifier)
    
    async def _fetch_openapi_spec(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch OpenAPI specification from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'json' in content_type:
                            return await response.json()
                        elif 'yaml' in content_type or 'yml' in content_type:
                            text = await response.text()
                            return yaml.safe_load(text)
                        else:
                            # Try to parse as JSON first, then YAML
                            text = await response.text()
                            try:
                                return json.loads(text)
                            except:
                                return yaml.safe_load(text)
        except Exception as e:
            self.logger.debug(f"Failed to fetch spec from {url}: {e}")
            return None
    
    async def _search_public_api_specs(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Search for public API specifications"""
        # This would integrate with APIs.io, RapidAPI, or other API directories
        # For now, return a mock response for demo purposes
        
        mock_specs = {
            "github": {
                "openapi": "3.0.0",
                "info": {"title": "GitHub API", "version": "v3"},
                "servers": [{"url": "https://api.github.com"}],
                "paths": {
                    "/user": {
                        "get": {
                            "summary": "Get authenticated user",
                            "responses": {"200": {"description": "User object"}}
                        }
                    },
                    "/repos/{owner}/{repo}": {
                        "get": {
                            "summary": "Get repository",
                            "parameters": [
                                {"name": "owner", "in": "path", "required": True},
                                {"name": "repo", "in": "path", "required": True}
                            ]
                        }
                    }
                }
            },
            "notion": {
                "openapi": "3.0.0",
                "info": {"title": "Notion API", "version": "2022-06-28"},
                "servers": [{"url": "https://api.notion.com/v1"}],
                "paths": {
                    "/pages": {
                        "post": {
                            "summary": "Create page",
                            "requestBody": {"required": True}
                        }
                    },
                    "/databases/{database_id}/query": {
                        "post": {
                            "summary": "Query database",
                            "parameters": [
                                {"name": "database_id", "in": "path", "required": True}
                            ]
                        }
                    }
                }
            }
        }
        
        return mock_specs.get(service_name.lower())
    
    async def _parse_api_specification(self, api_docs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenAPI specification into structured format"""
        parsed = {
            "service_info": {
                "title": api_docs.get("info", {}).get("title", "Unknown Service"),
                "version": api_docs.get("info", {}).get("version", "1.0"),
                "description": api_docs.get("info", {}).get("description", ""),
                "base_url": ""
            },
            "endpoints": [],
            "authentication": {},
            "schemas": api_docs.get("components", {}).get("schemas", {})
        }
        
        # Extract base URL
        servers = api_docs.get("servers", [])
        if servers:
            parsed["service_info"]["base_url"] = servers[0].get("url", "")
        
        # Parse authentication
        security_schemes = api_docs.get("components", {}).get("securitySchemes", {})
        parsed["authentication"] = security_schemes
        
        # Parse endpoints
        paths = api_docs.get("paths", {})
        for path, methods in paths.items():
            for method, spec in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = APIEndpoint(
                        endpoint_id=f"{method}_{path}".replace("/", "_").replace("{", "").replace("}", ""),
                        url=path,
                        method=method.upper(),
                        parameters=self._extract_parameters(spec),
                        description=spec.get("summary", spec.get("description", "")),
                        response_schema=spec.get("responses", {}),
                        authentication=spec.get("security", [])
                    )
                    parsed["endpoints"].append(endpoint)
        
        return parsed
    
    def _extract_parameters(self, endpoint_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from endpoint specification"""
        parameters = {
            "path": [],
            "query": [],
            "header": [],
            "body": None
        }
        
        # Extract parameters
        for param in endpoint_spec.get("parameters", []):
            param_info = {
                "name": param.get("name"),
                "type": param.get("schema", {}).get("type", "string"),
                "required": param.get("required", False),
                "description": param.get("description", "")
            }
            
            param_location = param.get("in", "query")
            if param_location in parameters:
                parameters[param_location].append(param_info)
        
        # Extract request body
        request_body = endpoint_spec.get("requestBody", {})
        if request_body:
            content = request_body.get("content", {})
            if "application/json" in content:
                parameters["body"] = content["application/json"].get("schema", {})
        
        return parameters
    
    async def _generate_service_integration(self, service_id: str, parsed_spec: Dict[str, Any], 
                                          auth_config: Optional[Dict[str, Any]]) -> ServiceIntegration:
        """Generate complete service integration"""
        service_info = parsed_spec["service_info"]
        
        # Generate capabilities based on endpoints
        capabilities = []
        for endpoint in parsed_spec["endpoints"]:
            capability_name = self._generate_capability_name(endpoint)
            capabilities.append(capability_name)
        
        # Generate agent code
        agent_code = await self._generate_agent_code(service_id, parsed_spec)
        
        return ServiceIntegration(
            service_id=service_id,
            service_name=service_info["title"],
            base_url=service_info["base_url"],
            api_version=service_info["version"],
            endpoints=parsed_spec["endpoints"],
            authentication_config=auth_config or {},
            capabilities=capabilities,
            generated_agent_code=agent_code,
            created_at=datetime.now()
        )
    
    def _generate_capability_name(self, endpoint: APIEndpoint) -> str:
        """Generate human-readable capability name from endpoint"""
        # Simple name generation based on HTTP method and path
        path_parts = [part for part in endpoint.url.split("/") if part and not part.startswith("{")]
        
        if endpoint.method == "GET":
            action = "get" if len(path_parts) > 1 else "list"
        elif endpoint.method == "POST":
            action = "create"
        elif endpoint.method == "PUT" or endpoint.method == "PATCH":
            action = "update"
        elif endpoint.method == "DELETE":
            action = "delete"
        else:
            action = endpoint.method.lower()
        
        resource = "_".join(path_parts) if path_parts else "resource"
        return f"{action}_{resource}"
    
    async def _generate_agent_code(self, service_id: str, parsed_spec: Dict[str, Any]) -> str:
        """Generate Python agent code for the service"""
        service_info = parsed_spec["service_info"]
        endpoints = parsed_spec["endpoints"]
        
        # Generate imports and class definition
        code_parts = [
            '"""',
            f'Auto-generated agent for {service_info["title"]}',
            f'Generated on: {datetime.now().isoformat()}',
            '"""',
            '',
            'import asyncio',
            'import aiohttp',
            'import logging',
            'from typing import Dict, List, Optional, Any',
            'from datetime import datetime',
            '',
            'from core.orchestrator import BaseAgent, AgentType, Task, AgentCapability',
            '',
            '',
            f'class {self._to_class_name(service_id)}Agent(BaseAgent):',
            f'    """Auto-generated agent for {service_info["title"]}"""',
            '',
            '    def __init__(self):',
            f'        super().__init__(AgentType.INTEGRATION)',
            f'        self.service_name = "{service_info["title"]}"',
            f'        self.base_url = "{service_info["base_url"]}"',
            '        self.session = None',
            '',
            '        # Auto-generated capabilities',
            '        self.capabilities = ['
        ]
        
        # Generate capabilities
        for endpoint in endpoints:
            capability_name = self._generate_capability_name(endpoint)
            code_parts.append(f'            AgentCapability("{capability_name}", "{endpoint.description}", '
                            f'[], [], "intermediate", "medium"),')
        
        code_parts.extend([
            '        ]',
            '',
            '    async def execute_task(self, task: Task) -> Dict[str, Any]:',
            '        """Execute API tasks"""',
            '        try:',
            '            if not self.session:',
            '                self.session = aiohttp.ClientSession()',
            '',
            '            action = task.parameters.get("action")',
            ''
        ])
        
        # Generate action handlers
        for endpoint in endpoints:
            capability_name = self._generate_capability_name(endpoint)
            method_name = f'_{capability_name}'
            
            code_parts.extend([
                f'            if action == "{capability_name}":',
                f'                return await self.{method_name}(task.parameters)',
            ])
        
        code_parts.extend([
            '',
            '            return {"error": "Unknown action", "status": "failed"}',
            '',
            '        except Exception as e:',
            '            return {"error": str(e), "status": "failed"}',
            ''
        ])
        
        # Generate individual method implementations
        for endpoint in endpoints:
            capability_name = self._generate_capability_name(endpoint)
            method_name = f'_{capability_name}'
            
            code_parts.extend([
                f'    async def {method_name}(self, params: Dict[str, Any]) -> Dict[str, Any]:',
                f'        """Execute {endpoint.description}"""',
                f'        url = self.base_url + "{endpoint.url}"',
                '',
                '        # Replace path parameters',
                '        for key, value in params.items():',
                '            url = url.replace("{" + key + "}", str(value))',
                '',
                '        # Prepare request',
                f'        method = "{endpoint.method}"',
                '        headers = {"Content-Type": "application/json"}',
                '        data = None',
                '',
                '        if method in ["POST", "PUT", "PATCH"]:',
                '            data = params.get("body", {})',
                '',
                '        # Make request',
                '        async with self.session.request(method, url, json=data, headers=headers) as response:',
                '            result = await response.json() if response.content_type == "application/json" else await response.text()',
                '            return {',
                '                "status": "success" if response.status < 400 else "error",',
                '                "status_code": response.status,',
                '                "data": result',
                '            }',
                ''
            ])
        
        return '\n'.join(code_parts)
    
    def _to_class_name(self, service_id: str) -> str:
        """Convert service ID to valid Python class name"""
        # Remove non-alphanumeric characters and capitalize
        clean_name = ''.join(c for c in service_id if c.isalnum() or c == '_')
        return ''.join(word.capitalize() for word in clean_name.split('_'))
    
    async def _generate_agent_wrapper(self, integration: ServiceIntegration) -> BaseAgent:
        """Generate and instantiate agent wrapper"""
        # Save the generated code to a file
        agent_file = self.integrations_dir / f"{integration.service_id}_agent.py"
        
        with open(agent_file, 'w') as f:
            f.write(integration.generated_agent_code)
        
        # Dynamically import and instantiate the agent
        spec = importlib.util.spec_from_file_location(
            f"{integration.service_id}_agent", 
            agent_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the agent class
        agent_class_name = f"{self._to_class_name(integration.service_id)}Agent"
        agent_class = getattr(module, agent_class_name)
        
        # Instantiate the agent
        return agent_class()
    
    async def _save_integration(self, integration: ServiceIntegration):
        """Save integration configuration"""
        config_file = self.integrations_dir / f"{integration.service_id}_config.json"
        
        config_data = {
            "service_id": integration.service_id,
            "service_name": integration.service_name,
            "base_url": integration.base_url,
            "api_version": integration.api_version,
            "capabilities": integration.capabilities,
            "created_at": integration.created_at.isoformat(),
            "endpoints_count": len(integration.endpoints)
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _load_agent_template(self) -> str:
        """Load agent code generation template"""
        # This would load from a template file in production
        return ""
    
    async def execute_service_action(self, service_id: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action on integrated service"""
        if service_id not in self.generated_agents:
            return {"error": f"Service {service_id} not integrated", "status": "failed"}
        
        agent = self.generated_agents[service_id]
        
        # Create task for the agent
        task = Task(
            task_id=f"api_call_{datetime.now().timestamp()}",
            description=f"Execute {action} on {service_id}",
            agent_type=AgentType.INTEGRATION,
            parameters={
                "action": action,
                **parameters
            },
            priority="medium",
            created_at=datetime.now()
        )
        
        # Execute the task
        return await agent.execute_task(task)
    
    async def list_integrations(self) -> Dict[str, Any]:
        """List all available integrations"""
        return {
            "integrations": [
                {
                    "service_id": integration.service_id,
                    "service_name": integration.service_name,
                    "capabilities": integration.capabilities,
                    "endpoints_count": len(integration.endpoints),
                    "created_at": integration.created_at.isoformat()
                }
                for integration in self.integrations.values()
            ],
            "total_count": len(self.integrations)
        }
    
    async def natural_language_command(self, command: str) -> Dict[str, Any]:
        """Execute natural language commands across integrated services"""
        # This would use NLP to parse commands and route to appropriate services
        # For now, simple keyword matching
        
        command_lower = command.lower()
        
        # GitHub commands
        if "github" in command_lower:
            if "create repo" in command_lower or "new repository" in command_lower:
                return await self.execute_service_action("github", "create_repos", {
                    "body": {"name": "new-repo", "private": False}
                })
            elif "get repo" in command_lower or "show repository" in command_lower:
                return await self.execute_service_action("github", "get_repos", {
                    "owner": "user",
                    "repo": "repo-name"
                })
        
        # Notion commands  
        elif "notion" in command_lower:
            if "create page" in command_lower or "new page" in command_lower:
                return await self.execute_service_action("notion", "create_pages", {
                    "body": {"parent": {"database_id": "example"}, "properties": {}}
                })
        
        return {
            "error": "Could not understand command or service not integrated",
            "suggestion": "Try: 'integrate with github' or 'create github repo'",
            "status": "failed"
        }


class IntegrationOrchestrator:
    """Orchestrates all API integrations and manages service ecosystem"""
    
    def __init__(self):
        self.api_engine = UniversalAPIEngine()
        self.logger = logging.getLogger("nova.integration_orchestrator")
        
        # Service ecosystem
        self.connected_services: Dict[str, Dict[str, Any]] = {}
        self.service_workflows: List[Dict[str, Any]] = []
    
    async def auto_integrate_user_services(self, user_services: List[str]) -> Dict[str, Any]:
        """Automatically integrate with all user's digital services"""
        results = {
            "successful_integrations": [],
            "failed_integrations": [],
            "total_capabilities": 0
        }
        
        for service in user_services:
            try:
                result = await self.api_engine.integrate_service(service)
                
                if result["success"]:
                    results["successful_integrations"].append({
                        "service": service,
                        "capabilities": result["capabilities"],
                        "endpoints": result["endpoints_count"]
                    })
                    results["total_capabilities"] += len(result["capabilities"])
                else:
                    results["failed_integrations"].append({
                        "service": service,
                        "error": result["error"]
                    })
                    
            except Exception as e:
                results["failed_integrations"].append({
                    "service": service,
                    "error": str(e)
                })
        
        return results
    
    async def create_service_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create automated workflows across multiple services"""
        workflow = {
            "name": workflow_name,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "workflow_id": f"workflow_{len(self.service_workflows)}"
        }
        
        self.service_workflows.append(workflow)
        
        return {
            "workflow_created": True,
            "workflow_id": workflow["workflow_id"],
            "steps_count": len(steps)
        }
    
    async def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a cross-service workflow"""
        workflow = next((w for w in self.service_workflows if w["workflow_id"] == workflow_id), None)
        
        if not workflow:
            return {"error": "Workflow not found", "status": "failed"}
        
        results = []
        
        for step in workflow["steps"]:
            service_id = step["service"]
            action = step["action"]
            step_params = {**step.get("parameters", {}), **(parameters or {})}
            
            result = await self.api_engine.execute_service_action(service_id, action, step_params)
            results.append({
                "step": step["name"],
                "service": service_id,
                "result": result
            })
            
            # Stop workflow if step fails
            if result.get("status") == "failed":
                break
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "steps_executed": len(results),
            "results": results
        }
