from agents.registry import AgentRegistry
from agents.code_generator_agent import CodeGeneratorAgent
from project_builder import ProjectBuilder


class AgentOrchestrator:
    """
    Central controller responsible for coordinating
    multiple AI agents and building the final project.
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    # ---------------------------------------------------------
    # DISPLAY HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _print_section(title: str):
        """Print a clean section header."""

        print()
        print("=" * 64)
        print(f" {title}")
        print("=" * 64)

    @staticmethod
    def _print_agent_output(agent_name: str, output: str):
        """Display an agent's response in a clean format."""

        print()
        print("-" * 64)
        print(f" {agent_name}")
        print("-" * 64)
        print()
        print(output.strip())
        print()

    # ---------------------------------------------------------
    # MAIN WORKFLOW
    # ---------------------------------------------------------

    def run(self, request: str):
        """
        Execute the complete multi-agent development workflow.
        """

        # -----------------------------------------------------
        # WORKFLOW START
        # -----------------------------------------------------

        self._print_section("MULTI-AGENT WORKFLOW")

        print()
        print("USER REQUEST")
        print("-" * 64)
        print(request.strip())

        print()
        print("Starting AI development team...")
        print()

        # -----------------------------------------------------
        # STEP 1: MANAGER AGENT
        # -----------------------------------------------------

        manager = self.registry.get("manager")

        if manager is None:
            raise ValueError(
                "Manager Agent is not registered."
            )

        print("[1/5] MANAGER AGENT")
        print("-" * 64)
        print("Status : ANALYZING REQUIREMENT...")

        development_plan = manager.run(request)

        print("Status : COMPLETED")

        self._print_agent_output(
            "MANAGER DEVELOPMENT PLAN",
            development_plan
        )

        # -----------------------------------------------------
        # STEP 2: DEVELOPER AGENT
        # -----------------------------------------------------

        developer = self.registry.get("developer")

        if developer is None:
            raise ValueError(
                "Developer Agent is not registered."
            )

        print("[2/5] DEVELOPER AGENT")
        print("-" * 64)
        print("Status : CREATING TECHNICAL PLAN...")

        developer_plan = developer.run(development_plan)

        print("Status : COMPLETED")

        self._print_agent_output(
            "DEVELOPER TECHNICAL PLAN",
            developer_plan
        )

        # -----------------------------------------------------
        # STEP 3: BACKEND AGENT
        # -----------------------------------------------------

        backend = self.registry.get("backend")

        if backend is None:
            raise ValueError(
                "Backend Agent is not registered."
            )

        print("[3/5] BACKEND AGENT")
        print("-" * 64)
        print("Status : DESIGNING BACKEND...")

        backend_plan = backend.run(developer_plan)

        print("Status : COMPLETED")

        self._print_agent_output(
            "BACKEND IMPLEMENTATION PLAN",
            backend_plan
        )

        # -----------------------------------------------------
        # STEP 4: CODE GENERATOR
        # -----------------------------------------------------

        code_generator = self.registry.get("code_generator")

        if code_generator is None:
            raise ValueError(
                "Code Generator Agent is not registered."
            )

        print("[4/5] CODE GENERATOR AGENT")
        print("-" * 64)
        print("Status : GENERATING SOURCE CODE...")

        generated_code = code_generator.run(
            backend_plan
        )

        print("Status : COMPLETED")

        # We don't print the complete generated source code here.
        # This keeps the terminal clean and professional.

        # -----------------------------------------------------
        # STEP 5: PROJECT BUILDER
        # -----------------------------------------------------

        print()
        print("[5/5] PROJECT BUILDER")
        print("-" * 64)
        print("Status : CREATING PROJECT FILES...")

        project_builder = ProjectBuilder(
            "generated_project"
        )

        created_files = project_builder.build(
            generated_code
        )

        print("Status : COMPLETED")

        # -----------------------------------------------------
        # WORKFLOW COMPLETE
        # -----------------------------------------------------

        self._print_section("WORKFLOW COMPLETE")

        print()
        print("AGENTS EXECUTED")
        print("-" * 64)
        print("✓ Manager Agent")
        print("✓ Developer Agent")
        print("✓ Backend Agent")
        print("✓ Code Generator Agent")
        print("✓ Project Builder")

        print()
        print("GENERATED FILES")
        print("-" * 64)

        for file_path in created_files:
            print(f"✓ {file_path}")

        print()
        print("WORKFLOW STATUS")
        print("-" * 64)
        print("✓ Requirement analyzed")
        print("✓ Development plan generated")
        print("✓ Technical plan generated")
        print("✓ Backend plan generated")
        print("✓ Source code generated")
        print("✓ Project files created")

        print()
        print("System Status : READY")
        print()

        return {
            "request": request,
            "development_plan": development_plan,
            "developer_plan": developer_plan,
            "backend_plan": backend_plan,
            "generated_code": generated_code,
            "created_files": created_files,
        }