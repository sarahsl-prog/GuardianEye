"""Threat Hunting Agent for proactive threat detection."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import THREAT_HUNTING_PROMPT


class ThreatHuntingAgent(BaseAgent):
    """Agent for generating threat hunting hypotheses and investigations."""

    def __init__(self, llm):
        """Initialize threat hunting agent."""
        super().__init__(llm, name="threat_hunting")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for threat hunting."""
        return ChatPromptTemplate.from_messages([
            ("system", THREAT_HUNTING_PROMPT),
            ("user", """Hunting Context: {context}
            Known Threats: {known_threats}

            Please generate threat hunting hypotheses and investigation steps.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process threat hunting request.

        Args:
            input_data: Threat hunting context

        Returns:
            AgentOutput with hunting hypotheses
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        context = input_data.context.get("hunting_context", input_data.query)
        known_threats = input_data.context.get("known_threats", "No specific threats identified")

        # Execute
        response = await chain.ainvoke({
            "context": context,
            "known_threats": known_threats
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "has_known_threats": "known_threats" in input_data.context,
            }
        )
