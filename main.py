import warnings

from dotenv import load_dotenv

from agents.manager_agent import ManagerAgent
from agents.developer_agent import DeveloperAgent
from agents.backend_agent import BackendAgent
from agents.code_generator_agent import CodeGeneratorAgent
from agents.registry import AgentRegistry
from agents.orchestrator import AgentOrchestrator


# ---------------------------------------------------------
# SUPPRESS UNNECESSARY LIBRARY WARNINGS
# ---------------------------------------------------------

warnings.filterwarnings(
    "ignore",
    message="Model .* uses fixed sampling defaults.*"
)

warnings.filterwarnings(
    "ignore",
    message="Direct use of automatic function calling.*"
)


class MultiAgentWorkflow:
    """
    Main application workflow for the Multi-Agent AI Employee.
    """

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # -------------------------------------------------
        # CREATE AGENT REGISTRY
        # -------------------------------------------------

        self.registry = AgentRegistry()

        # -------------------------------------------------
        # CREATE AI AGENTS
        # -------------------------------------------------

        manager = ManagerAgent(provider="gemini")
        developer = DeveloperAgent(provider="gemini")
        backend = BackendAgent(provider="gemini")
        code_generator = CodeGeneratorAgent(provider="gemini")

        # -------------------------------------------------
        # REGISTER AI AGENTS
        # -------------------------------------------------

        self.registry.register("manager", manager)
        self.registry.register("developer", developer)
        self.registry.register("backend", backend)
        self.registry.register("code_generator", code_generator)

        # -------------------------------------------------
        # CREATE ORCHESTRATOR
        # -------------------------------------------------

        self.orchestrator = AgentOrchestrator(self.registry)

    def run(self, request: str):
        """
        Start the multi-agent workflow.
        """

        return self.orchestrator.run(request)


def print_header():
    """
    Display the application header.
    """

    print()
    print("=" * 64)
    print("                 MULTI-AGENT AI EMPLOYEE")
    print("=" * 64)
    print()
    print("  AI-powered software development team")
    print("  Manager • Developer • Backend • Code Generator")
    print()
    print("-" * 64)


def main():
    """
    Main entry point of the application.
    """

    # -----------------------------------------------------
    # APPLICATION HEADER
    # -----------------------------------------------------

    print_header()

    # -----------------------------------------------------
    # GET USER REQUIREMENT
    # -----------------------------------------------------

    print()
    print("USER REQUEST")
    print("-" * 64)

    request = input(
        "What software do you want to build?\n> "
    ).strip()

    # -----------------------------------------------------
    # VALIDATE INPUT
    # -----------------------------------------------------

    if not request:
        print()
        print("-" * 64)
        print("ERROR: No software requirement was provided.")
        print("Please enter a valid software requirement.")
        print("-" * 64)
        return

    # -----------------------------------------------------
    # DISPLAY REQUEST
    # -----------------------------------------------------

    print()
    print("-" * 64)
    print("REQUEST RECEIVED")
    print("-" * 64)
    print(request)
    print()

    # -----------------------------------------------------
    # CREATE WORKFLOW
    # -----------------------------------------------------

    workflow = MultiAgentWorkflow()

    # -----------------------------------------------------
    # START MULTI-AGENT WORKFLOW
    # -----------------------------------------------------

    workflow.run(request)


if __name__ == "__main__":
    main()