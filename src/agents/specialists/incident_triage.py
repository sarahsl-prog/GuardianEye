"""Incident Triage Agent for analyzing security alerts."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import Field

from src.agents.base.base_agent import BaseAgent, AgentInput, AgentOutput
from src.core.prompts import INCIDENT_TRIAGE_PROMPT


class IncidentTriageInput(AgentInput):
    """Input for incident triage agent."""

    alert_details: str = Field(..., description="Raw alert details")
    severity: str = Field(default="medium", description="Alert severity level")


class IncidentTriageOutput(AgentOutput):
    """Output from incident triage agent."""

    summary: str = Field(default="", description="Incident summary")
    suggested_actions: list[str] = Field(
        default_factory=list, description="Recommended actions"
    )
    priority: str = Field(default="medium", description="Priority level")


class IncidentTriageAgent(BaseAgent):
    """Agent for analyzing security incidents and suggesting responses."""

    def __init__(self, llm):
        """Initialize the Incident Triage Agent.

        Args:
            llm: Language model instance
        """
        super().__init__(llm, name="incident_triage")

    def get_prompt_template(self) -> str:
        """Return the prompt template for this agent."""
        return INCIDENT_TRIAGE_PROMPT

    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process incident triage request.

        Args:
            input_data: Input containing alert details

        Returns:
            Triage analysis with recommendations
        """
        # Extract fields from input
        alert_details = input_data.context.get("alert_details", input_data.query)
        severity = input_data.context.get("severity", "medium")

        # Create prompt
        prompt = ChatPromptTemplate.from_template(self.get_prompt_template())

        # Create chain
        chain = prompt | self.llm | StrOutputParser()

        # Execute
        response = await chain.ainvoke({
            "alert_details": alert_details,
            "severity": severity
        })

        # Parse response and extract information
        lines = response.strip().split('\n')
        summary = response[:200] + "..." if len(response) > 200 else response
        suggested_actions = [
            line.strip('- ').strip()
            for line in lines
            if line.strip().startswith('-') or line.strip().startswith('•')
        ][:5]

        return IncidentTriageOutput(
            result=response,
            summary=summary,
            suggested_actions=suggested_actions or ["Review alert details", "Investigate further"],
            priority="high" if "critical" in response.lower() else "medium",
            metadata={
                "agent": self.name,
                "model": getattr(self.llm, "model_name", "unknown"),
                "severity": severity
            }
        )
