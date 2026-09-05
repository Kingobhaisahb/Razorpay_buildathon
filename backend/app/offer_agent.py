import os
import asyncio
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
from sqlalchemy import select

from .database import AsyncSessionLocal
from .analytics import get_business_metrics
from .models import AIAction


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

gemini_client = genai.Client(
    api_key=api_key
)


# ============================================================
# GEMINI RESPONSE SCHEMA
# ============================================================

class OfferAIRecommendation(BaseModel):

    opportunity: str

    reasoning: str

    hypothesis: str

    recommended_action: str

    expected_impact: str

    confidence: float = Field(
        ge=0,
        le=1
    )

    requires_approval: bool


# ============================================================
# DETERMINISTIC OFFER AGENT
# ============================================================

def analyze_offer_opportunities(
    metrics: Dict[str, Any]
) -> Dict[str, Any]:

    products = metrics.get(
        "product_performance",
        []
    )

    opportunities = []

    for product in products:

        views = product.get(
            "views",
            0
        )

        conversion_rate = product.get(
            "conversion_rate",
            0
        )

        margin = product.get(
            "margin_percent",
            0
        )

        inventory = product.get(
            "inventory",
            0
        )

        price = product.get(
            "price",
            0
        )

        # ----------------------------------------------------
        # FILTERING
        # ----------------------------------------------------

        if views < 500:
            continue

        if conversion_rate >= 2.0:
            continue

        if margin < 25:
            continue

        if inventory < 10:
            continue

        # ----------------------------------------------------
        # OPPORTUNITY SCORE
        # ----------------------------------------------------

        traffic_score = min(
            views / 1000,
            10
        )

        conversion_gap = max(
            0,
            2.0 - conversion_rate
        )

        margin_score = min(
            margin / 10,
            10
        )

        score = (
            traffic_score
            + conversion_gap * 2
            + margin_score
        )

        # ----------------------------------------------------
        # RECOMMENDED DISCOUNT
        # ----------------------------------------------------

        if margin >= 40:
            recommended_discount = 10.0

        elif margin >= 30:
            recommended_discount = 7.0

        else:
            recommended_discount = 5.0

        recommended_discount = min(
            recommended_discount,
            15.0
        )

        # ----------------------------------------------------
        # DISCOUNTED PRICE
        # ----------------------------------------------------

        discounted_price = price * (
            1 - recommended_discount / 100
        )

        cost = product.get(
            "cost",
            0
        )

        # ----------------------------------------------------
        # REMAINING MARGIN
        # ----------------------------------------------------

        if discounted_price > 0:

            remaining_margin = (
                (discounted_price - cost)
                / discounted_price
            ) * 100

        else:

            remaining_margin = 0

        # ----------------------------------------------------
        # FINAL SAFETY CHECK
        # ----------------------------------------------------

        if remaining_margin < 25:
            continue

        product_name = product.get(
            "product_name"
        )

        # ----------------------------------------------------
        # CREATE OPPORTUNITY
        # ----------------------------------------------------

        opportunity = {

            "type": "product_offer",

            "severity": (
                "high"
                if score >= 15
                else "medium"
            ),

            "score": round(
                score,
                2
            ),

            "product_id": product.get(
                "product_id"
            ),

            "product_name": product_name,

            "evidence": [

                f"Views: {views}",

                f"Conversion rate: "
                f"{conversion_rate:.2f}%",

                f"Current margin: "
                f"{margin:.2f}%",

                f"Inventory: {inventory}",
            ],

            "hypothesis": (
                "The product receives significant "
                "traffic but has relatively low "
                "conversion despite having sufficient "
                "margin and inventory."
            ),

            "recommended_discount_percent":
                recommended_discount,

            "discounted_price":
                round(
                    discounted_price,
                    2
                ),

            "remaining_margin_percent":
                round(
                    remaining_margin,
                    2
                ),

            "recommended_action": (
                f"Test a "
                f"{recommended_discount:.0f}% "
                f"targeted offer on "
                f"{product_name}."
            ),
        }

        opportunities.append(
            opportunity
        )

    # --------------------------------------------------------
    # SORT OPPORTUNITIES
    # --------------------------------------------------------

    opportunities.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {

        "opportunity_detected":
            len(opportunities) > 0,

        "primary_opportunity": (
            opportunities[0]
            if opportunities
            else None
        ),

        "opportunities":
            opportunities,
    }


# ============================================================
# GEMINI AI REASONING
# ============================================================

async def generate_ai_offer_recommendation(
    analysis: Dict[str, Any]
) -> OfferAIRecommendation:

    primary = analysis.get(
        "primary_opportunity"
    )

    if not primary:

        return OfferAIRecommendation(

            opportunity="No offer opportunity detected.",

            reasoning=(
                "Current product analytics do not "
                "identify a product that satisfies "
                "the offer criteria."
            ),

            hypothesis="No actionable offer opportunity.",

            recommended_action="No action required.",

            expected_impact="No measurable impact expected.",

            confidence=1.0,

            requires_approval=False,
        )

    prompt = f"""
You are the Offer Optimization Agent inside ShopControl,
an autonomous AI growth platform for online merchants.

Your job is to reason about a product promotion opportunity.

IMPORTANT RULES:

1. The numerical metrics below were calculated by a
   deterministic analytics engine.

2. Do NOT change, invent, or recalculate the numbers.

3. Do NOT recommend a discount larger than the
   deterministic recommendation.

4. The merchant requires approval before activating
   a promotional offer.

5. Your job is to explain WHY this opportunity exists,
   formulate a useful hypothesis, and recommend a
   controlled experiment.

PRODUCT OPPORTUNITY:

Product ID:
{primary.get("product_id")}

Product:
{primary.get("product_name")}

Views:
{primary.get("evidence")[0]}

Conversion:
{primary.get("evidence")[1]}

Current Margin:
{primary.get("evidence")[2]}

Inventory:
{primary.get("evidence")[3]}

Deterministic Opportunity Score:
{primary.get("score")}

Recommended Discount:
{primary.get("recommended_discount_percent")}%

Discounted Price:
₹{primary.get("discounted_price")}

Remaining Margin:
{primary.get("remaining_margin_percent")}%

Deterministic Hypothesis:
{primary.get("hypothesis")}

Produce a concise business recommendation.

Explain the opportunity, likely reason for low conversion,
and how the merchant should test the offer safely.

The response must follow the provided JSON schema.
"""

    interaction = await gemini_client.aio.interactions.create(

        model="gemini-3.6-flash",

        input=prompt,

        response_format=[
            {
                "type": "text",
                "mime_type": "application/json",
                "schema":
                    OfferAIRecommendation.model_json_schema(),
            }
        ],
    )

    return OfferAIRecommendation.model_validate_json(
        interaction.output_text
    )


# ============================================================
# SAVE AI ACTION
# ============================================================

async def save_ai_action(
    recommendation: OfferAIRecommendation,
    analysis: Dict[str, Any]
):

    primary = analysis.get(
        "primary_opportunity"
    )

    if not primary:
        return None

    async with AsyncSessionLocal() as session:

        action = AIAction(

            merchant_id=1,

            agent_name="Offer Agent",

            action_type="offer_recommendation",

            description=(
                recommendation.recommended_action
            ),

            status=(
                "approval_required"
                if recommendation.requires_approval
                else "ready"
            ),

            expected_impact=0.0,

            actual_impact=0.0,
        )

        session.add(action)

        await session.commit()

        await session.refresh(action)

        return action.id


# ============================================================
# RUN OFFER AGENT
# ============================================================

async def run_offer_agent():

    async with AsyncSessionLocal() as session:

        metrics = await get_business_metrics(
            session
        )

    deterministic_analysis = (
        analyze_offer_opportunities(
            metrics
        )
    )

    ai_recommendation = (
        await generate_ai_offer_recommendation(
            deterministic_analysis
        )
    )

    action_id = await save_ai_action(
        ai_recommendation,
        deterministic_analysis
    )

    return (
        deterministic_analysis,
        ai_recommendation,
        action_id
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    (
        deterministic_analysis,
        ai_recommendation,
        action_id
    ) = asyncio.run(
        run_offer_agent()
    )

    print(
        "\n=============================="
    )

    print(
        "DETERMINISTIC OFFER ANALYSIS"
    )

    print(
        "=============================="
    )

    print(
        deterministic_analysis
    )

    print(
        "\n=============================="
    )

    print(
        "GEMINI AI OFFER RECOMMENDATION"
    )

    print(
        "=============================="
    )

    print(
        ai_recommendation.model_dump_json(
            indent=4
        )
    )

    print(
        "\n=============================="
    )

    print(
        "AI ACTION CREATED"
    )

    print(
        "=============================="
    )

    print(
        f"AI Action ID: {action_id}"
    )