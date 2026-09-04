from typing import Dict, Any


def analyze_checkout_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze checkout analytics and identify the strongest
    revenue opportunity for the Checkout Agent.

    The calculations are deterministic.
    AI reasoning will be added after this layer.
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
            "severity": "high" if device_conversion_gap >= 8 else "medium",
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

            if best_method is None or success_rate > best_method["success_rate"]:
                best_method = {
                    "method": method,
                    "success_rate": success_rate
                }

            if worst_method is None or success_rate < worst_method["success_rate"]:
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
                    "severity": "high" if payment_gap >= 10 else "medium",
                    "score": payment_gap,
                    "evidence": [
                        f"{best_method['method']} success rate: "
                        f"{best_method['success_rate']}%",
                        f"{worst_method['method']} success rate: "
                        f"{worst_method['success_rate']}%",
                        f"Payment success gap: {round(payment_gap, 2)}%"
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
    # 3. OVERALL CHECKOUT FAILURE
    # =====================================================

    abandonment_rate = checkout_data.get("abandonment_rate", 0)
    failure_rate = checkout_data.get("failure_rate", 0)

    if abandonment_rate >= 20:
        opportunities.append({
            "type": "checkout_abandonment",
            "severity": "high",
            "score": abandonment_rate,
            "evidence": [
                f"Checkout abandonment rate: {abandonment_rate}%"
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

    if failure_rate >= 15:
        opportunities.append({
            "type": "payment_failure",
            "severity": "high",
            "score": failure_rate,
            "evidence": [
                f"Checkout failure rate: {failure_rate}%"
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
    # 4. SELECT STRONGEST OPPORTUNITY
    # =====================================================

    if not opportunities:
        return {
            "opportunity_detected": False,
            "message": "No significant checkout opportunity detected.",
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

if __name__ == "__main__":
    import asyncio
    from .database import AsyncSessionLocal
    from .analytics import get_business_metrics

    async def test_agent():
        async with AsyncSessionLocal() as session:
            metrics = await get_business_metrics(session)

            result = analyze_checkout_metrics(metrics)

            print("\n==============================")
            print("CHECKOUT AGENT RESULT")
            print("==============================")

            print(result)

    asyncio.run(test_agent())