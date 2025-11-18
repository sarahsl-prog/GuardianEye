"""Reconnaissance Orchestrator Agent for information gathering."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import RECON_ORCHESTRATOR_PROMPT


class ReconOrchestratorAgent(BaseAgent):
    """Agent for orchestrating reconnaissance activities."""

    def __init__(self, llm):
        """Initialize the Recon Orchestrator Agent."""
        super().__init__(llm, name="recon_orchestrator")

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return RECON_ORCHESTRATOR_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process reconnaissance orchestration request."""
        target = input_data.context.get("target", "")
        objectives = input_data.context.get("objectives", input_data.query)

        prompt = ChatPromptTemplate.from_template(self.get_prompt_template())
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "target": target,
            "objectives": objectives
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown"),
                "target": target
            }
        )
