import os
import math
import random
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
# NORMAL DISTRIBUTION CDF
# ============================================

def normal_cdf(value: float) -> float:
    """
    Standard normal cumulative distribution function.
    """

    return 0.5 * (
        1 + math.erf(value / math.sqrt(2))
    )


# ============================================
# TWO-PROPORTION Z-TEST
# ============================================

def calculate_p_value(
    control_visitors: int,
    control_conversions: int,
    variant_visitors: int,
    variant_conversions: int
) -> float:

    if control_visitors <= 0 or variant_visitors <= 0:
        return 1.0

    control_rate = (
        control_conversions / control_visitors
    )

    variant_rate = (
        variant_conversions / variant_visitors
    )

    pooled_rate = (
        (control_conversions + variant_conversions)
        / (control_visitors + variant_visitors)
    )

    standard_error = math.sqrt(
        pooled_rate
        * (1 - pooled_rate)
        * (
            (1 / control_visitors)
            + (1 / variant_visitors)
        )
    )

    if standard_error == 0:
        return 1.0

    z_score = (
        variant_rate - control_rate
    ) / standard_error

    p_value = 2 * (
        1 - normal_cdf(abs(z_score))
    )

    return max(0.0, min(1.0, p_value))


# ============================================
# SIMULATE EXPERIMENT RESULTS
# ============================================

def simulate_experiment_results(
    baseline_conversion: float,
    expected_lift: float = 0.15,
    visitors_per_arm: int = 200000
) -> Dict[str, Any]:

    random.seed()

    # ----------------------------------------
    # CONTROL
    # ----------------------------------------

    control_visitors = visitors_per_arm

    control_rate = baseline_conversion / 100

    control_conversions = round(
        control_visitors * control_rate
    )

    # ----------------------------------------
    # VARIANT
    # ----------------------------------------

    variation = random.uniform(
        -0.02,
        0.02
    )

    variant_rate = (
        control_rate
        * (1 + expected_lift + variation)
    )

    variant_rate = min(
        variant_rate,
        0.99
    )

    variant_visitors = visitors_per_arm

    variant_conversions = round(
        variant_visitors * variant_rate
    )

    # ----------------------------------------
    # ACTUAL CONVERSION RATES
    # ----------------------------------------

    control_conversion = (
        control_conversions
        / control_visitors
        * 100
    )

    variant_conversion = (
        variant_conversions
        / variant_visitors
        * 100
    )

    # ----------------------------------------
    # RELATIVE CONVERSION LIFT
    # ----------------------------------------

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

    # ----------------------------------------
    # STATISTICAL SIGNIFICANCE
    # ----------------------------------------

    p_value = calculate_p_value(
        control_visitors,
        control_conversions,
        variant_visitors,
        variant_conversions
    )

    statistically_significant = (
        p_value < 0.05
    )

    return {
        "control_visitors": control_visitors,

        "variant_visitors": variant_visitors,

        "control_conversions": control_conversions,

        "variant_conversions": variant_conversions,

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
        ),

        "p_value": round(
            p_value,
            4
        ),

        "statistically_significant": (
            statistically_significant
        )
    }


# ============================================
# DETERMINE EXPERIMENT RESULT
# ============================================

def determine_experiment_result(
    conversion_lift: float,
    p_value: float,
    statistically_significant: bool
) -> Dict[str, Any]:

    # ----------------------------------------
    # VARIANT WINS
    # ----------------------------------------

    if (
        conversion_lift >= 10
        and statistically_significant
        and p_value < 0.05
    ):

        return {
            "status": "completed",
            "winner": "variant",
            "decision": "deploy_variant"
        }

    # ----------------------------------------
    # CONTROL WINS
    # ----------------------------------------

    if (
        conversion_lift <= -10
        and statistically_significant
        and p_value < 0.05
    ):

        return {
            "status": "completed",
            "winner": "control",
            "decision": "keep_control"
        }

    # ----------------------------------------
    # NOT ENOUGH EVIDENCE
    # ----------------------------------------

    return {
        "status": "continue_testing",
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

Control visitors:
{results["control_visitors"]}

Variant visitors:
{results["variant_visitors"]}

Control conversions:
{results["control_conversions"]}

Variant conversions:
{results["variant_conversions"]}

Control conversion:
{results["control_conversion"]}%

Variant conversion:
{results["variant_conversion"]}%

Conversion lift:
{results["conversion_lift"]}%

P-value:
{results["p_value"]}

Statistically significant:
{results["statistically_significant"]}

DETERMINISTIC DECISION:

Winner:
{decision["winner"]}

Decision:
{decision["decision"]}

Return a structured recommendation.

The confidence value must represent confidence
in the recommendation based only on the provided evidence.

If the variant won and the result is statistically significant,
recommend deployment but state that merchant approval is required.

If the control won, recommend keeping the control.

If the result is not statistically significant,
recommend continuing the experiment rather than deploying a winner.
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

            control_visitors=(
                experiment_data["control_visitors"]
            ),

            variant_visitors=(
                experiment_data["variant_visitors"]
            ),

            control_conversions=(
                experiment_data["control_conversions"]
            ),

            variant_conversions=(
                experiment_data["variant_conversions"]
            ),

            control_conversion=(
                experiment_data["control_conversion"]
            ),

            variant_conversion=(
                experiment_data["variant_conversion"]
            ),

            control_revenue=(
                experiment_data.get(
                    "control_revenue",
                    0.0
                )
            ),

            variant_revenue=(
                experiment_data.get(
                    "variant_revenue",
                    0.0
                )
            ),

            conversion_lift=(
                experiment_data["conversion_lift"]
            ),

            revenue_lift=(
                experiment_data.get(
                    "revenue_lift",
                    0.0
                )
            ),

            p_value=(
                experiment_data["p_value"]
            ),

            statistically_significant=(
                experiment_data[
                    "statistically_significant"
                ]
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
            metrics[
                "payment_method_performance"
            ]
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
        expected_lift=0.15,
        visitors_per_arm=200000
    )

    print("\nExperiment Results:")
    print(results)

    # ----------------------------------------
    # 5. DETERMINE WINNER
    # ----------------------------------------

    decision = determine_experiment_result(
        conversion_lift=results["conversion_lift"],
        p_value=results["p_value"],
        statistically_significant=(
            results["statistically_significant"]
        )
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

        "control_revenue": 0.0,
        "variant_revenue": 0.0,
        "revenue_lift": 0.0,

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