import os
from typing import Dict, Any

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field
from sqlalchemy import select

from .database import AsyncSessionLocal
from .models import Experiment
from .analytics import get_business_metrics


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

class ABTestAIRecommendation(BaseModel):
    opportunity: str
    reasoning: str
    conclusion: str
    recommended_action: str
    expected_impact: str
    confidence: float = Field(ge=0, le=1)
    requires_approval: bool


# ============================================
# CREATE EXPERIMENT HYPOTHESIS
# ============================================

def create_experiment_hypothesis(
    opportunity: Dict[str, Any]
) -> Dict[str, Any]:

    opportunity_type = opportunity.get("type")

    if opportunity_type == "product_offer":

        product_name = opportunity.get("product_name")
        discount = opportunity.get(
            "recommended_discount_percent",
            0
        )

        return {
            "name": f"{product_name} {discount}% Offer Test",

            "hypothesis": (
                f"Offering a {discount}% targeted discount on "
                f"{product_name} will increase conversion while "
                f"maintaining acceptable margins."
            ),

            "control": "Current product experience",

            "variant": f"{discount}% targeted discount"
        }

    if opportunity_type == "mobile_checkout":

        return {
            "name": "Mobile Checkout Optimization Test",

            "hypothesis": (
                "A streamlined mobile checkout and payment "
                "experience will increase mobile checkout conversion."
            ),

            "control": "Current mobile checkout",

            "variant": "Optimized mobile checkout"
        }

    if opportunity_type == "payment_method":

        payment_method = opportunity.get(
            "payment_method",
            "upi"
        )

        return {
            "name": (
                f"{payment_method.upper()} Payment "
                f"Optimization Test"
            ),

            "hypothesis": (
                f"Optimizing the {payment_method} payment flow "
                "will increase successful payment conversion."
            ),

            "control": "Current payment flow",

            "variant": "Optimized payment flow"
        }

    return {
        "name": "Commerce Optimization Test",

        "hypothesis": (
            "The proposed optimization will improve "
            "checkout conversion without negatively "
            "affecting merchant revenue."
        ),

        "control": "Current experience",

        "variant": "Optimized experience"
    }


# ============================================
# SIMULATE EXPERIMENT RESULTS
# ============================================

def simulate_experiment_results(
    baseline_conversion: float,
    expected_lift: float = 0.15
) -> Dict[str, Any]:

    import random

    random.seed()

    control_conversion = baseline_conversion

    variation = random.uniform(
        -0.02,
        0.02
    )

    variant_conversion = (
        baseline_conversion
        * (1 + expected_lift + variation)
    )

    variant_conversion = min(
        variant_conversion,
        100
    )

    conversion_lift = (
        (
            variant_conversion
            - control_conversion
        )
        / control_conversion
        * 100
        if control_conversion > 0
        else 0
    )

    return {
        "control_conversion": round(
            control_conversion,
            2
        ),

        "variant_conversion": round(
            variant_conversion,
            2
        ),

        "conversion_lift": round(
            conversion_lift,
            2
        )
    }


# ============================================
# DETERMINE EXPERIMENT RESULT
# ============================================

def determine_experiment_result(
    conversion_lift: float
) -> Dict[str, Any]:

    if conversion_lift >= 10:

        return {
            "status": "completed",
            "winner": "variant",
            "decision": "deploy_variant"
        }

    if conversion_lift <= -10:

        return {
            "status": "completed",
            "winner": "control",
            "decision": "keep_control"
        }

    return {
        "status": "completed",
        "winner": "neutral",
        "decision": "continue_testing"
    }


# ============================================
# GEMINI A/B TEST REASONING
# ============================================

async def generate_ai_ab_test_recommendation(
    experiment: Dict[str, Any],
    results: Dict[str, Any],
    decision: Dict[str, Any]
) -> ABTestAIRecommendation:

    prompt = f"""
You are the A/B Testing intelligence layer of an
autonomous AI growth platform for online merchants.

Analyze the experiment using ONLY the provided data.

Your job is to explain:
1. What the experiment tested.
2. What happened.
3. Why the result matters.
4. Whether the merchant should deploy the variant,
   keep the control, or continue testing.

Do NOT invent metrics.

Do NOT calculate new metrics beyond the provided values.

The deterministic experiment engine is the source of truth.

EXPERIMENT:

Name:
{experiment["name"]}

Hypothesis:
{experiment["hypothesis"]}

Control:
{experiment["control"]}

Variant:
{experiment["variant"]}

RESULTS:

Control conversion:
{results["control_conversion"]}%

Variant conversion:
{results["variant_conversion"]}%

Conversion lift:
{results["conversion_lift"]}%

DETERMINISTIC DECISION:

Winner:
{decision["winner"]}

Decision:
{decision["decision"]}

Return a structured recommendation.

The confidence value must represent confidence
in the recommendation based on the evidence provided.

If the result is positive and the deterministic
engine selected the variant, recommend deployment
but state that merchant approval is required.

If the control won, recommend keeping the control.

If the result is neutral, recommend continuing
the experiment rather than deploying a winner.
"""

    interaction = await gemini_client.aio.interactions.create(
        model="gemini-3.6-flash",

        input=prompt,

        response_format=[
            {
                "type": "text",
                "mime_type": "application/json",
                "schema": ABTestAIRecommendation.model_json_schema(),
            }
        ]
    )

    return ABTestAIRecommendation.model_validate_json(
        interaction.output_text
    )


# ============================================
# SAVE EXPERIMENT
# ============================================

async def save_experiment(
    experiment_data: Dict[str, Any]
) -> int:

    async with AsyncSessionLocal() as session:

        experiment = Experiment(
            merchant_id=1,

            name=experiment_data["name"],

            hypothesis=experiment_data["hypothesis"],

            control_conversion=(
                experiment_data["control_conversion"]
            ),

            variant_conversion=(
                experiment_data["variant_conversion"]
            ),

            status=experiment_data["status"],

            winner=experiment_data["winner"]
        )

        session.add(experiment)

        await session.commit()

        await session.refresh(experiment)

        return experiment.id


# ============================================
# RUN A/B TESTING AGENT
# ============================================

async def run_ab_testing_agent(
    opportunity: Dict[str, Any]
) -> Dict[str, Any]:

    print("\n==============================")
    print("A/B TESTING AGENT")
    print("==============================")

    # ----------------------------------------
    # 1. CREATE HYPOTHESIS
    # ----------------------------------------

    experiment = create_experiment_hypothesis(
        opportunity
    )

    print("\nExperiment:")
    print(experiment)

    # ----------------------------------------
    # 2. GET BUSINESS METRICS
    # ----------------------------------------

    async with AsyncSessionLocal() as session:

        metrics = await get_business_metrics(
            session
        )

    # ----------------------------------------
    # 3. DETERMINE BASELINE
    # ----------------------------------------

    opportunity_type = opportunity.get(
        "type"
    )

    if opportunity_type == "mobile_checkout":

        baseline_conversion = (
            metrics["device_performance"]
            ["mobile"]
            ["conversion_rate"]
        )

    elif opportunity_type == "payment_method":

        payment_method = opportunity.get(
            "payment_method",
            "upi"
        )

        baseline_conversion = (
            metrics["payment_method_performance"]
            .get(
                payment_method,
                metrics["payments"]
            )
            ["success_rate"]
        )

    else:

        baseline_conversion = opportunity.get(
            "conversion_rate",
            1.0
        )

    # ----------------------------------------
    # 4. RUN EXPERIMENT
    # ----------------------------------------

    results = simulate_experiment_results(
        baseline_conversion=baseline_conversion,
        expected_lift=0.15
    )

    print("\nExperiment Results:")
    print(results)

    # ----------------------------------------
    # 5. DETERMINE WINNER
    # ----------------------------------------

    decision = determine_experiment_result(
        results["conversion_lift"]
    )

    print("\nDecision:")
    print(decision)

    # ----------------------------------------
    # 6. GEMINI REASONING
    # ----------------------------------------

    print("\n==============================")
    print("GEMINI A/B TEST REASONING")
    print("==============================")

    ai_recommendation = (
        await generate_ai_ab_test_recommendation(
            experiment=experiment,
            results=results,
            decision=decision
        )
    )

    print(
        ai_recommendation.model_dump_json(
            indent=4
        )
    )

    # ----------------------------------------
    # 7. SAVE EXPERIMENT
    # ----------------------------------------

    experiment_record = {
        **experiment,
        **results,
        "status": decision["status"],
        "winner": decision["winner"]
    }

    experiment_id = await save_experiment(
        experiment_record
    )

    print("\n==============================")
    print("EXPERIMENT CREATED")
    print("==============================")

    print(
        f"Experiment ID: {experiment_id}"
    )

    return {
        "experiment_id": experiment_id,

        "experiment": experiment,

        "results": results,

        "decision": decision,

        "ai_recommendation": (
            ai_recommendation.model_dump()
        )
    }


# ============================================
# TEST
# ============================================

async def main():

    opportunity = {
        "type": "product_offer",

        "product_id": 8,

        "product_name": "Wireless Earbuds 8",

        "conversion_rate": 0.24,

        "recommended_discount_percent": 10.0
    }

    result = await run_ab_testing_agent(
        opportunity
    )

    print("\n==============================")
    print("FINAL RESULT")
    print("==============================")

    print(result)


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())