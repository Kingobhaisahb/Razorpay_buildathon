import os
from typing import Dict, Any, List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

from .database import AsyncSessionLocal
from .analytics import get_business_metrics
from .checkout_agent import analyze_checkout_metrics
from .offer_agent import analyze_offer_opportunities


# ============================================
# GEMINI CONFIGURATION
# ============================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================
# GEMINI RESPONSE SCHEMA
# ============================================

class GrowthRecommendation(BaseModel):

    business_summary: str

    top_opportunity: str

    reasoning: str

    priority: str

    recommended_action: str

    expected_impact: str

    confidence: float = Field(
        ge=0,
        le=1
    )

    requires_approval: bool


# ============================================
# PRIORITY SCORING
# ============================================

def calculate_priority_score(
    opportunity: Dict[str, Any]
) -> float:

    severity = opportunity.get(
        "severity",
        "medium"
    )

    score = opportunity.get(
        "score",
        0
    )

    severity_multiplier = {
        "critical": 2.0,
        "high": 1.5,
        "medium": 1.0,
        "low": 0.5
    }.get(
        severity,
        1.0
    )

    return score * severity_multiplier


# ============================================
# COLLECT GROWTH OPPORTUNITIES
# ============================================

async def collect_growth_opportunities(
    metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:

    opportunities = []

    # ========================================
    # CHECKOUT AGENT
    # ========================================

    checkout_analysis = analyze_checkout_metrics(
        metrics
    )

    if checkout_analysis.get(
        "opportunity_detected"
    ):

        for opportunity in checkout_analysis.get(
            "opportunities",
            []
        ):

            opportunities.append({
                "source_agent": "Checkout Agent",
                **opportunity
            })

    # ========================================
    # OFFER AGENT
    # ========================================

    offer_analysis = analyze_offer_opportunities(
        metrics
    )

    if offer_analysis.get(
        "opportunity_detected"
    ):

        for opportunity in offer_analysis.get(
            "opportunities",
            []
        ):

            opportunities.append({
                "source_agent": "Offer Agent",
                **opportunity
            })

    # ========================================
    # PRIORITY SCORING
    # ========================================

    for opportunity in opportunities:

        opportunity["priority_score"] = (
            round(
                calculate_priority_score(
                    opportunity
                ),
                2
            )
        )

    # ========================================
    # SORT
    # ========================================

    opportunities.sort(
        key=lambda item: item[
            "priority_score"
        ],
        reverse=True
    )

    return opportunities


# ============================================
# GEMINI CHIEF GROWTH REASONING
# ============================================

async def generate_growth_recommendation(
    metrics: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> GrowthRecommendation:

    prompt = f"""
You are the Chief Growth AI of ShopControl,
an autonomous AI growth platform for online merchants.

Your responsibility is to determine which detected
business opportunity should receive the highest priority.

The deterministic analytics engine and specialized
agents are the source of truth.

DO NOT invent metrics.

DO NOT modify provided numbers.

DO NOT calculate new metrics.

Prioritize based on:
- severity
- opportunity score
- business relevance
- available evidence
- financial safety

Any action that changes pricing, offers, checkout,
or merchant-facing behavior requires approval.

You are an ORCHESTRATOR.

You do not directly execute actions.

BUSINESS METRICS:

{metrics}

DETECTED OPPORTUNITIES:

{opportunities}

Return a structured recommendation.

Explain:

1. Overall business situation.
2. Most important opportunity.
3. Why it should be prioritized.
4. Recommended next action.
5. Expected business impact.
6. Whether merchant approval is required.

Keep the answer concise and practical.
"""

    interaction = await gemini_client.aio.interactions.create(
        model="gemini-3.6-flash",

        input=prompt,

        response_format=[
            {
                "type": "text",
                "mime_type": "application/json",
                "schema": GrowthRecommendation.model_json_schema(),
            }
        ]
    )

    return GrowthRecommendation.model_validate_json(
        interaction.output_text
    )


# ============================================
# CHIEF GROWTH AGENT
# ============================================

async def run_chief_growth_agent():

    print("\n")
    print("=" * 60)
    print("             CHIEF GROWTH AGENT")
    print("=" * 60)

    # ========================================
    # 1. LOAD BUSINESS METRICS
    # ========================================

    print("\n[1] ANALYZING BUSINESS METRICS...")

    async with AsyncSessionLocal() as session:

        metrics = await get_business_metrics(
            session
        )

    print("✓ Business metrics loaded")

    # ========================================
    # 2. RUN SPECIALIZED ANALYTICS
    # ========================================

    print("\n[2] CONSULTING SPECIALIZED AGENTS...")

    opportunities = (
        await collect_growth_opportunities(
            metrics
        )
    )

    print(
        f"✓ {len(opportunities)} opportunities detected"
    )

    # ========================================
    # 3. DISPLAY OPPORTUNITIES
    # ========================================

    print("\n[3] DETECTED GROWTH OPPORTUNITIES")

    for index, opportunity in enumerate(
        opportunities,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{opportunity.get('type')}"
        )

        print(
            f"   Agent: "
            f"{opportunity.get('source_agent')}"
        )

        print(
            f"   Severity: "
            f"{opportunity.get('severity')}"
        )

        print(
            f"   Score: "
            f"{opportunity.get('score')}"
        )

        print(
            f"   Priority: "
            f"{opportunity.get('priority_score')}"
        )

        print(
            f"   Action: "
            f"{opportunity.get('recommended_action')}"
        )

    # ========================================
    # 4. HANDLE NO OPPORTUNITIES
    # ========================================

    if not opportunities:

        print("\nNo significant opportunities found.")

        return {
            "status": "no_opportunities",
            "business_metrics": metrics,
            "opportunities": []
        }

    # ========================================
    # 5. CHIEF GROWTH AI
    # ========================================

    print("\n[4] CHIEF GROWTH AI REASONING")

    recommendation = (
        await generate_growth_recommendation(
            metrics,
            opportunities
        )
    )

    print(
        recommendation.model_dump_json(
            indent=4
        )
    )

    # ========================================
    # 6. FINAL RESULT
    # ========================================

    result = {

        "status": "opportunities_detected",

        "business_metrics": metrics,

        "opportunities": opportunities,

        "recommendation": (
            recommendation.model_dump()
        )
    }

    print("\n")
    print("=" * 60)
    print("             GROWTH DECISION")
    print("=" * 60)

    print(
        f"\nTop Opportunity:\n"
        f"{recommendation.top_opportunity}"
    )

    print(
        f"\nPriority:\n"
        f"{recommendation.priority}"
    )

    print(
        f"\nRecommended Action:\n"
        f"{recommendation.recommended_action}"
    )

    print(
        f"\nConfidence:\n"
        f"{recommendation.confidence}"
    )

    print(
        f"\nRequires Approval:\n"
        f"{recommendation.requires_approval}"
    )

    return result


# ============================================
# TEST
# ============================================

async def main():

    result = await run_chief_growth_agent()

    print("\n")
    print("=" * 60)
    print("             FINAL RESULT")
    print("=" * 60)

    print(result)


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())