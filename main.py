# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from nmap_manager import NmapManager # Your Task 3/4 Manager
# import uvicorn

# app = FastAPI(title="NMAP-AI Chatbot API")

# # 1. Enable CORS (Allows your Frontend to talk to this Backend)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], # In production, replace with your frontend URL
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 2. Initialize the NMAP-AI Manager
# manager = NmapManager()

# # 3. Define the Data Structure for the Chat
# class ChatRequest(BaseModel):
#     intent: str
#     target: str

# # 4. The Main Chat Endpoint
# @app.post("/chat")
# async def chat_with_agent(request: ChatRequest):
#     try:
#         # Run the NMAP-AI Pipeline
#         result = manager.execute_pipeline(request.intent, request.target)
        
#         # Return the result to the frontend
#         return {
#             "status": "success",
#             "category": result["category"],
#             "command": result["command"],
#             "is_valid": result["is_valid"],
#             "is_functional": result.get("is_functional", False),
#             "mcp_report": result.get("mcp_report", "No report generated.")
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # 5. Health Check
# @app.get("/")
# async def root():
#     return {"message": "NMAP-AI API is running!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    
    
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from nmap_manager import NmapManager
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# --- Models ---
class ChatRequest(BaseModel):
    intent: str
    target: str

# --- FastAPI App ---
app = FastAPI(title="NMAP-AI Open API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = NmapManager()

@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        # No auth check, direct execution
        result = manager.execute_pipeline(request.intent, request.target)
        return {
            "status": "success",
            "category": result["category"],
            "command": result["command"],
            "is_valid": result["is_valid"],
            "error": result.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "NMAP-AI API is running in OPEN mode!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
