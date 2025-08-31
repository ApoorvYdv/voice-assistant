from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from src.core.workflows.supervisor import SupervisorWorkflow

copilotkit_remote_endpoint = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="voice-assistant",
            description="Voice assistant for day to day task agent",
            graph=SupervisorWorkflow().supervisor(),
        )
    ],
    actions=[],
)
