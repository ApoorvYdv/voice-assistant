from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from src.core.workflows.supervisor import SupervisorWorkflow

supervisor = SupervisorWorkflow()
copilotkit_remote_endpoint = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="voice-assistant",
            description="Voice assistant for day to day task agent",
            graph=SupervisorWorkflow().supervisor(),
            config=SupervisorWorkflow().get_config(),
        )
    ],
    actions=[],
)
