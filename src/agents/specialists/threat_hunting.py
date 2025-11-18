"""Threat Hunting Agent for proactive threat detection."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import THREAT_HUNTING_PROMPT


class ThreatHuntingAgent(BaseAgent):
    """Agent for proactive threat hunting and hypothesis generation."""

    def __init__(self, llm):
        """Initialize the Threat Hunting Agent."""
        super().__init__(llm, name="threat_hunting")

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return THREAT_HUNTING_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process threat hunting request."""
        context = input_data.context.get("context", input_data.query)

        prompt = ChatPromptTemplate.from_template(self.get_prompt_template())
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({"context": context})

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown"),
                "hunt_type": "proactive"
            }
        )
