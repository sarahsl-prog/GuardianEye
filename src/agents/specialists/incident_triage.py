"""Incident Triage Agent for analyzing security incidents."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field

from src.agents.base.base_agent import AgentInput, AgentOutput, BaseAgent
from src.core.prompts import INCIDENT_TRIAGE_PROMPT


class IncidentTriageInput(AgentInput):
    """Input schema for incident triage agent."""

    alert_details: str = Field(..., description="Raw alert details")
    alert_severity: str = Field(default="medium", description="Alert severity level")


class IncidentTriageAgent(BaseAgent):
    """Agent for analyzing security incidents and suggesting responses."""

    def __init__(self, llm):
        """Initialize incident triage agent."""
        super().__init__(llm, name="incident_triage")
        self.parser = StrOutputParser()

    def get_prompt_template(self) -> ChatPromptTemplate:
        """Get prompt template for incident triage."""
        return ChatPromptTemplate.from_messages([
            ("system", INCIDENT_TRIAGE_PROMPT),
            ("user", """Alert Details: {alert_details}
            Severity: {alert_severity}

            Please analyze this incident and provide your assessment.""")
        ])

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """
        Process incident triage request.

        Args:
            input_data: Incident details

        Returns:
            AgentOutput with triage results
        """
        # Create chain
        chain = self.get_prompt_template() | self.llm | self.parser

        # Prepare input
        alert_details = input_data.context.get("alert_details", input_data.query)
        alert_severity = input_data.context.get("alert_severity", "medium")

        # Execute
        response = await chain.ainvoke({
            "alert_details": alert_details,
            "alert_severity": alert_severity
        })

        return AgentOutput(
            result=response,
            metadata={
                "agent": self.name,
                "severity": alert_severity,
            }
        )
