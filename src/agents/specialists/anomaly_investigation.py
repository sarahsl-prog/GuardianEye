"""Anomaly Investigation Agent for detecting unusual patterns."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import ANOMALY_INVESTIGATION_PROMPT


class AnomalyInvestigationAgent(BaseAgent):
    """Agent for investigating anomalies and unusual behaviors."""

    def __init__(self, llm):
        """Initialize the Anomaly Investigation Agent."""
        super().__init__(llm, name="anomaly_investigation")

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return ANOMALY_INVESTIGATION_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process anomaly investigation request."""
        log_data = input_data.context.get("log_data", input_data.query)
        baseline = input_data.context.get("baseline", "normal operating parameters")

        prompt = ChatPromptTemplate.from_template(self.get_prompt_template())
        chain = prompt | self.llm | StrOutputParser()

        response = await chain.ainvoke({
            "log_data": log_data,
            "baseline": baseline
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown")
            }
        )
