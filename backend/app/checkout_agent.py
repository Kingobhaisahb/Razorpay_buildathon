import os
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


# =====================================================
# GEMINI CONFIGURATION
# =====================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

gemini_client = genai.Client(api_key=api_key)


# =====================================================
# AI RESPONSE SCHEMA
# =====================================================

class CheckoutAIRecommendation(BaseModel):

    opportunity: str = Field(
        description="The checkout opportunity identified by the AI."
    )

    reasoning: str = Field(
        description="Why this opportunity matters based only on the provided evidence."
    )

    hypothesis: str = Field(
        description="A testable hypothesis explaining the likely cause."
    )

    recommended_action: str = Field(
        description="The recommended next action for the merchant."
    )

    expected_impact: str = Field(
        description="A qualitative estimate of the potential business impact."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="AI confidence in the recommendation, from 0 to 1."
    )

    requires_approval: bool = Field(
        description="Whether the recommended action should require merchant approval."
    )


# =====================================================
# DETERMINISTIC CHECKOUT ANALYSIS
# =====================================================

def analyze_checkout_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze checkout analytics and identify the strongest
    revenue opportunity for the Checkout Agent.

    The calculations are deterministic.
    AI reasoning happens in a separate layer.
    """

    device_data = metrics.get("device_performance", {})
    payment_data = metrics.get("payment_method_performance", {})
    checkout_data = metrics.get("checkout", {})

    opportunities = []

    # =====================================================
    # 1. DEVICE PERFORMANCE
    # =====================================================

    mobile = device_data.get("mobile", {})
    desktop = device_data.get("desktop", {})

    mobile_conversion = mobile.get("conversion_rate", 0)
    desktop_conversion = desktop.get("conversion_rate", 0)

    mobile_payment_success = mobile.get("payment_success_rate", 0)

    device_conversion_gap = desktop_conversion - mobile_conversion

    if device_conversion_gap >= 5:

        opportunities.append({
            "type": "mobile_checkout",

            "severity": (
                "high"
                if device_conversion_gap >= 8
                else "medium"
            ),

            "score": device_conversion_gap,

            "evidence": [
                f"Mobile conversion: {mobile_conversion}%",
                f"Desktop conversion: {desktop_conversion}%",
                f"Mobile payment success: {mobile_payment_success}%"
            ],

            "hypothesis": (
                "Mobile customers may be experiencing additional "
                "checkout or payment friction."
            ),

            "recommended_action": (
                "Run an A/B test optimizing the mobile checkout "
                "experience and payment flow."
            )
        })


    # =====================================================
    # 2. PAYMENT METHOD PERFORMANCE
    # =====================================================

    if payment_data:

        best_method = None
        worst_method = None

        for method, data in payment_data.items():

            success_rate = data.get("success_rate", 0)

            # Find best payment method
            if (
                best_method is None
                or success_rate > best_method["success_rate"]
            ):
                best_method = {
                    "method": method,
                    "success_rate": success_rate
                }

            # Find worst payment method
            if (
                worst_method is None
                or success_rate < worst_method["success_rate"]
            ):
                worst_method = {
                    "method": method,
                    "success_rate": success_rate
                }


        if best_method and worst_method:

            payment_gap = (
                best_method["success_rate"]
                - worst_method["success_rate"]
            )

            if payment_gap >= 5:

                opportunities.append({
                    "type": "payment_method",

                    "severity": (
                        "high"
                        if payment_gap >= 10
                        else "medium"
                    ),

                    "score": payment_gap,

                    "evidence": [
                        f"{best_method['method']} success rate: "
                        f"{best_method['success_rate']}%",

                        f"{worst_method['method']} success rate: "
                        f"{worst_method['success_rate']}%",

                        f"Payment success gap: "
                        f"{round(payment_gap, 2)}%"
                    ],

                    "hypothesis": (
                        f"The {worst_method['method']} payment method "
                        "may be causing avoidable payment failures."
                    ),

                    "recommended_action": (
                        f"Investigate and optimize the "
                        f"{worst_method['method']} payment experience."
                    )
                })


    # =====================================================
    # 3. OVERALL CHECKOUT ABANDONMENT
    # =====================================================

    abandonment_rate = checkout_data.get(
        "abandonment_rate",
        0
    )

    failure_rate = checkout_data.get(
        "failure_rate",
        0
    )


    if abandonment_rate >= 20:

        opportunities.append({
            "type": "checkout_abandonment",

            "severity": "high",

            "score": abandonment_rate,

            "evidence": [
                f"Checkout abandonment rate: "
                f"{abandonment_rate}%"
            ],

            "hypothesis": (
                "A significant percentage of customers leave "
                "during checkout before completing payment."
            ),

            "recommended_action": (
                "Run a checkout optimization experiment focused "
                "on reducing friction and abandonment."
            )
        })


    # =====================================================
    # 4. OVERALL PAYMENT FAILURE
    # =====================================================

    if failure_rate >= 15:

        opportunities.append({
            "type": "payment_failure",

            "severity": "high",

            "score": failure_rate,

            "evidence": [
                f"Checkout failure rate: "
                f"{failure_rate}%"
            ],

            "hypothesis": (
                "Payment failures may be causing measurable "
                "revenue leakage."
            ),

            "recommended_action": (
                "Investigate payment failures and test "
                "alternative payment experiences."
            )
        })


    # =====================================================
    # 5. SELECT STRONGEST OPPORTUNITY
    # =====================================================

    if not opportunities:

        return {
            "opportunity_detected": False,

            "message": (
                "No significant checkout opportunity detected."
            ),

            "opportunities": []
        }


    opportunities.sort(
        key=lambda opportunity: opportunity["score"],
        reverse=True
    )

    strongest = opportunities[0]


    return {
        "opportunity_detected": True,

        "primary_opportunity": strongest,

        "opportunities": opportunities
    }


# =====================================================
# GEMINI AI REASONING
# =====================================================

async def generate_ai_recommendation(
    analysis: Dict[str, Any]
) -> CheckoutAIRecommendation:

    primary = analysis.get(
        "primary_opportunity"
    )


    if not primary:

        raise ValueError(
            "No primary checkout opportunity found."
        )


    prompt = f"""
You are the Checkout Optimization Agent for ShopControl,
an autonomous AI growth platform for online merchants.

Your job is to reason about a detected checkout opportunity
and recommend the safest next step for the merchant.

IMPORTANT RULES:

1. Do not invent metrics.

2. Do not calculate new metrics unless they are directly
   derivable from the provided evidence.

3. Treat the deterministic analytics as the source of truth.

4. Do not claim that a problem is definitely caused by a
   specific factor. Use hypothesis language when the cause
   is uncertain.

5. Prefer controlled experiments over permanent changes.

6. Any action that changes the merchant's checkout experience
   should require merchant approval.

7. Do not directly execute any action.

8. Keep the recommendation concise and practical.

PRIMARY OPPORTUNITY:

Type:
{primary.get("type")}

Severity:
{primary.get("severity")}

Score:
{primary.get("score")}

Evidence:
{primary.get("evidence")}

Existing hypothesis:
{primary.get("hypothesis")}

Existing recommended action:
{primary.get("recommended_action")}

OTHER DETECTED OPPORTUNITIES:

{analysis.get("opportunities")}

Generate the structured recommendation.
"""


    interaction = await gemini_client.aio.interactions.create(

        model="gemini-3.6-flash",

        input=prompt,

        response_format=[
            {
                "type": "text",
                "mime_type": "application/json",
                "schema": (
                    CheckoutAIRecommendation
                    .model_json_schema()
                ),
            }
        ],
    )


    return CheckoutAIRecommendation.model_validate_json(
        interaction.output_text
    )


# =====================================================
# TEST CHECKOUT AGENT
# =====================================================

if __name__ == "__main__":

    import asyncio

    from .database import AsyncSessionLocal
    from .analytics import get_business_metrics


    async def test_agent():

        async with AsyncSessionLocal() as session:

            # -------------------------------------------------
            # STEP 1: GET ANALYTICS
            # -------------------------------------------------

            metrics = await get_business_metrics(
                session
            )


            # -------------------------------------------------
            # STEP 2: DETECT OPPORTUNITIES
            # -------------------------------------------------

            analysis = analyze_checkout_metrics(
                metrics
            )


            print("\n==============================")
            print("DETERMINISTIC CHECKOUT ANALYSIS")
            print("==============================")

            print(analysis)


            # -------------------------------------------------
            # STEP 3: AI REASONING
            # -------------------------------------------------

            if analysis["opportunity_detected"]:

                ai_result = await generate_ai_recommendation(
                    analysis
                )


                print("\n==============================")
                print("GEMINI AI RECOMMENDATION")
                print("==============================")


                print(
                    ai_result.model_dump_json(
                        indent=4
                    )
                )


    asyncio.run(
        test_agent()
    )