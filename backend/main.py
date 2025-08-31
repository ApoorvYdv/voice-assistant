import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.copilotkit.copilotkit import copilotkit_remote_endpoint

load_dotenv()

app = FastAPI(title="FastAPI voice assistant server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_fastapi_endpoint(
    app,
    copilotkit_remote_endpoint,
    "/copilotkit_remote",
    max_workers=10,
)


def main():
    """Run the uvicorn server"""
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


if __name__ == "__main__":
    main()
