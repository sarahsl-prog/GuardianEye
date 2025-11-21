"""Shared tools that can be used by agents."""

from typing import Any


def format_incident_summary(incident_data: dict[str, Any]) -> str:
    """
    Format incident data into a readable summary.

    Args:
        incident_data: Raw incident data

    Returns:
        Formatted incident summary
    """
    summary_parts = []

    if "alert_name" in incident_data:
        summary_parts.append(f"Alert: {incident_data['alert_name']}")

    if "severity" in incident_data:
        summary_parts.append(f"Severity: {incident_data['severity']}")

    if "timestamp" in incident_data:
        summary_parts.append(f"Time: {incident_data['timestamp']}")

    if "description" in incident_data:
        summary_parts.append(f"\nDescription: {incident_data['description']}")

    return "\n".join(summary_parts)


def extract_iocs(text: str) -> dict[str, list[str]]:
    """
    Extract Indicators of Compromise from text.

    Args:
        text: Text to extract IOCs from

    Returns:
        Dictionary of IOC types and values
    """
    import re

    iocs: dict[str, list[str]] = {
        "ip_addresses": [],
        "domains": [],
        "file_hashes": [],
        "urls": [],
    }

    # IP addresses (simplified pattern)
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    iocs["ip_addresses"] = list(set(re.findall(ip_pattern, text)))

    # Domains (simplified pattern)
    domain_pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"
    iocs["domains"] = list(set(re.findall(domain_pattern, text)))

    # SHA256 hashes
    hash_pattern = r"\b[a-fA-F0-9]{64}\b"
    iocs["file_hashes"] = list(set(re.findall(hash_pattern, text)))

    # URLs (simplified pattern)
    url_pattern = r"https?://[^\s]+"
    iocs["urls"] = list(set(re.findall(url_pattern, text)))

    return iocs


def calculate_risk_score(
    severity: str,
    exploitability: float,
    business_impact: float
) -> dict[str, Any]:
    """
    Calculate risk score based on multiple factors.

    Args:
        severity: Severity level (critical, high, medium, low)
        exploitability: Exploitability score (0.0 to 1.0)
        business_impact: Business impact score (0.0 to 1.0)

    Returns:
        Dictionary with risk score and priority
    """
    severity_weights = {
        "critical": 1.0,
        "high": 0.75,
        "medium": 0.5,
        "low": 0.25,
    }

    severity_weight = severity_weights.get(severity.lower(), 0.5)
    risk_score = (severity_weight * 0.4) + (exploitability * 0.3) + (business_impact * 0.3)

    if risk_score >= 0.8:
        priority = "critical"
    elif risk_score >= 0.6:
        priority = "high"
    elif risk_score >= 0.4:
        priority = "medium"
    else:
        priority = "low"

    return {
        "risk_score": round(risk_score, 2),
        "priority": priority,
        "severity_weight": severity_weight,
        "exploitability": exploitability,
        "business_impact": business_impact,
    }
