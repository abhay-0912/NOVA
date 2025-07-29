"""
NOVA FastAPI Web Interface

Provides REST API endpoints for web-based interaction with NOVA
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio
import logging
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model"""
    content: str
    type: str = "text"
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    type: str
    sources: Optional[List[str]] = None
    actions_taken: Optional[List[str]] = None
    agent_used: Optional[str] = None
    processing_time: Optional[float] = None


class SystemStatus(BaseModel):
    """System status model"""
    status: str
    uptime: str
    memory_usage: Dict[str, Any]
    active_agents: List[Dict[str, Any]]
    security_level: str
    threat_level: int


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.logger = logging.getLogger("nova.api.websocket")
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)


def create_nova_api(nova_brain) -> FastAPI:
    """Create and configure the NOVA FastAPI application"""
    
    app = FastAPI(
        title="NOVA API",
        description="Neural Omnipresent Virtual Assistant API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware for web clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # WebSocket connection manager
    manager = ConnectionManager()
    
    # Logger
    logger = logging.getLogger("nova.api")
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Root endpoint with simple web interface"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>NOVA - Neural Omnipresent Virtual Assistant</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #0a0a0a; color: #fff; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .logo { font-size: 3em; margin-bottom: 10px; }
                .subtitle { font-size: 1.2em; color: #888; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 40px 0; }
                .feature { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
                .feature h3 { color: #4CAF50; margin-top: 0; }
                .api-link { display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 5px; }
                .api-link:hover { background: #45a049; }
                .status { background: #1a1a1a; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #4CAF50; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🧠 NOVA</div>
                    <div class="subtitle">Neural Omnipresent Virtual Assistant</div>
                </div>
                
                <div class="status">
                    <strong>Status:</strong> ✅ NOVA is active and ready to assist
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>🤖 Multi-Agent System</h3>
                        <p>Specialized agents for research, development, cybersecurity, and more</p>
                    </div>
                    <div class="feature">
                        <h3>🔒 Security Core</h3>
                        <p>Real-time threat monitoring and protection</p>
                    </div>
                    <div class="feature">
                        <h3>🧠 Adaptive Learning</h3>
                        <p>Learns from interactions and evolves with you</p>
                    </div>
                    <div class="feature">
                        <h3>🌐 Omnichannel</h3>
                        <p>Access through web, CLI, desktop, and mobile</p>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="/docs" class="api-link">📚 API Documentation</a>
                    <a href="/status" class="api-link">📊 System Status</a>
                    <a href="/health" class="api-link">❤️ Health Check</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            status = await nova_brain.get_status()
            return {
                "status": "healthy" if status["state"] == "active" else "degraded",
                "timestamp": datetime.now().isoformat(),
                "version": "0.1.0",
                "nova_state": status["state"]
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")
    
    @app.get("/status", response_model=SystemStatus)
    async def get_system_status():
        """Get detailed system status"""
        try:
            status = await nova_brain.get_status()
            
            return SystemStatus(
                status=status["state"],
                uptime="0:00:00",  # Would calculate actual uptime
                memory_usage=status.get("memory_stats", {}),
                active_agents=status.get("active_agents", []),
                security_level=status.get("security_level", "unknown"),
                threat_level=0  # Would get from security system
            )
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            raise HTTPException(status_code=500, detail="Unable to get system status")
    
    @app.post("/chat", response_model=ChatResponse)
    async def chat_with_nova(message: ChatMessage):
        """Chat with NOVA"""
        try:
            start_time = datetime.now()
            
            # Prepare input for NOVA brain
            input_data = {
                "type": message.type,
                "content": message.content,
                "context": message.context or {},
                "user_id": message.user_id,
                "timestamp": start_time.isoformat()
            }
            
            # Process through NOVA brain
            response = await nova_brain.process_input(input_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ChatResponse(
                response=response.get("response", "I apologize, but I couldn't process your request."),
                type=response.get("type", "text"),
                sources=response.get("sources", []),
                actions_taken=response.get("actions_taken", []),
                agent_used=response.get("agent_used"),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Chat processing failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to process chat message")
    
    @app.post("/god-mode")
    async def god_mode_execution(instruction: Dict[str, str]):
        """Execute god mode instruction"""
        try:
            instruction_text = instruction.get("instruction", "")
            if not instruction_text:
                raise HTTPException(status_code=400, detail="Instruction is required")
            
            logger.info(f"🚀 God mode request: {instruction_text}")
            
            result = await nova_brain.god_mode(instruction_text)
            
            return {
                "status": "executed",
                "instruction": instruction_text,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"God mode execution failed: {e}")
            raise HTTPException(status_code=500, detail="God mode execution failed")
    
    @app.get("/personality")
    async def get_personality():
        """Get current personality settings"""
        try:
            status = await nova_brain.get_status()
            return {
                "current_personality": status.get("personality", "unknown"),
                "available_personalities": [
                    "professional", "casual", "hacker", "mentor", 
                    "creative", "analyst", "assistant"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get personality: {e}")
            raise HTTPException(status_code=500, detail="Failed to get personality")
    
    @app.post("/personality")
    async def set_personality(personality_data: Dict[str, str]):
        """Set personality mode"""
        try:
            personality = personality_data.get("personality", "")
            if not personality:
                raise HTTPException(status_code=400, detail="Personality is required")
            
            # This would call the personality engine
            # For now, return success
            return {
                "status": "updated",
                "personality": personality,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to set personality: {e}")
            raise HTTPException(status_code=500, detail="Failed to set personality")
    
    @app.get("/agents")
    async def get_agents():
        """Get information about available agents"""
        try:
            status = await nova_brain.get_status()
            agents = status.get("active_agents", [])
            
            return {
                "agents": agents,
                "total_agents": len(agents),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            raise HTTPException(status_code=500, detail="Failed to get agents")
    
    @app.get("/security")
    async def get_security_status():
        """Get security system status"""
        try:
            # This would get actual security status
            return {
                "threat_level": 0,
                "active_alerts": 0,
                "last_scan": datetime.now().isoformat(),
                "protection_active": True,
                "vpn_status": "inactive"
            }
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get security status")
    
    @app.post("/security/scan")
    async def trigger_security_scan():
        """Trigger a security scan"""
        try:
            # This would trigger actual security scan
            return {
                "status": "scan_initiated",
                "scan_id": f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to trigger security scan: {e}")
            raise HTTPException(status_code=500, detail="Failed to trigger security scan")
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time communication"""
        await manager.connect(websocket)
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message through NOVA
                input_data = {
                    "type": message_data.get("type", "text"),
                    "content": message_data.get("content", ""),
                    "context": message_data.get("context", {}),
                    "websocket": True
                }
                
                response = await nova_brain.process_input(input_data)
                
                # Send response back
                await manager.send_personal_message(
                    json.dumps(response), 
                    websocket
                )
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            manager.disconnect(websocket)
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup event"""
        logger.info("🚀 NOVA API server starting up...")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event"""
        logger.info("🔄 NOVA API server shutting down...")
    
    return app
