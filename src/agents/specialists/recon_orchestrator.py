"""Reconnaissance Orchestrator Agent for intelligence gathering."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import RECON_ORCHESTRATOR_PROMPT


class ReconOrchestratorAgent(BaseAgent):
    """Agent for coordinating reconnaissance activities."""

    def __init__(self, llm):
        """Initialize recon orchestrator agent."""
        super().__init__(llm, name="recon_orchestrator")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for recon orchestration."""
        return ChatPromptTemplate.from_messages([
            ("system", RECON_ORCHESTRATOR_PROMPT),
            ("user", """Reconnaissance Target: {target}
            Objective: {objective}

            Please coordinate reconnaissance activities and provide intelligence insights.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process reconnaissance orchestration request.

        Args:
            input_data: Recon target and objectives

        Returns:
            AgentOutput with recon plan
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        target = input_data.context.get("target", "Not specified")
        objective = input_data.context.get("objective", input_data.query)

        # Execute
        response = await chain.ainvoke({
            "target": target,
            "objective": objective
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "target": target,
            }
        )
