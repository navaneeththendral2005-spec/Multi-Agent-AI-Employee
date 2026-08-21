class AgentRegistry:
    """
    Central registry for all AI agents in the system.

    New agents can be registered here without changing
    the core workflow architecture.
    """

    def __init__(self):
        self.agents = {}

    def register(self, name: str, agent):
        """
        Register an AI agent.
        """
        self.agents[name] = agent

    def get(self, name: str):
        """
        Retrieve a registered agent by name.
        """
        return self.agents.get(name)

    def list_agents(self):
        """
        Return the names of all registered agents.
        """
        return list(self.agents.keys())