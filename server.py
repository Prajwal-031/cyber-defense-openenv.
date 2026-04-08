import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional
from env.environment import CyberIncidentEnv
from env.models import Observation, Action, EnvironmentState
from env.tasks import TASKS

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cyber Incident Response OpenEnv",
    description="A simulated environment for training AI agents as Blue Team defenders in cybersecurity incident response",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global environment instance
env_instance: Optional[CyberIncidentEnv] = None

class StepRequest(BaseModel):
    """Request model for stepping the environment"""
    action: Dict[str, Any]

class ResetRequest(BaseModel):
    """Request model for resetting the environment"""
    task_id: str = "easy"
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """Validate that task_id is one of the valid tasks"""
        if v not in TASKS:
            raise ValueError(f"Invalid task_id. Must be one of: {', '.join(TASKS.keys())}")
        return v

@app.get("/")
async def root():
    """Serve the main UI page"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Cyber Incident Response OpenEnv API is running", "status": "healthy"}

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    logger.info("Health check request received")
    return {"message": "Cyber Incident Response OpenEnv API is running", "status": "healthy"}

@app.post("/api/reset")
async def reset(request: ResetRequest = ResetRequest()):
    """Reset the environment to initial state for a specific task"""
    global env_instance
    try:
        logger.info(f"Resetting environment with task_id: {request.task_id}")
        env_instance = CyberIncidentEnv(task_id=request.task_id)
        obs = env_instance.reset()
        logger.info(f"Environment reset successful for task: {request.task_id}")
        return obs.dict()
    except Exception as e:
        logger.error(f"Error resetting environment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting environment: {str(e)}")

@app.post("/api/step")
async def step(request: StepRequest):
    """Execute one step in the environment with the given action"""
    global env_instance
    try:
        if env_instance is None:
            logger.warning("Step called without environment initialization")
            raise HTTPException(status_code=400, detail="Environment not initialized. Call /api/reset first.")
        
        logger.debug(f"Executing step with action: {request.action}")
        obs, reward, done, info = env_instance.step(request.action)
        logger.debug(f"Step executed. Reward: {reward}, Done: {done}")
        
        return {
            "observation": obs.dict(),
            "reward": float(reward),
            "done": bool(done),
            "info": info
        }
    except Exception as e:
        logger.error(f"Error during step execution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during step execution: {str(e)}")

@app.get("/api/state")
async def state():
    """Get the full internal state of the environment"""
    global env_instance
    try:
        if env_instance is None:
            logger.warning("State endpoint called without environment initialization")
            raise HTTPException(status_code=400, detail="Environment not initialized. Call /api/reset first.")
        
        logger.debug("State endpoint called")
        return env_instance.state().dict()
    except Exception as e:
        logger.error(f"Error retrieving state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving state: {str(e)}")

@app.get("/api/tasks")
async def get_tasks():
    """List all available tasks"""
    logger.info("Available tasks endpoint called")
    return {
        "tasks": [
            {
                "id": task_id,
                "name": task.name,
                "goal": task.goal,
                "max_steps": task.max_steps,
                "scenario": task.scenario.value
            }
            for task_id, task in TASKS.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
