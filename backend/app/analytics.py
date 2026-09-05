from typing import Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Order,
    CheckoutSession,
    Payment,
    Product,
    OrderItem,
)


async def get_business_metrics(
    session: AsyncSession,
) -> Dict[str, Any]:

    # ============================================================
    # BUSINESS METRICS
    # ============================================================

    revenue_result = await session.execute(
        select(
            func.coalesce(
                func.sum(Order.total_amount),
                0
            )
        ).where(
            Order.status == "completed"
        )
    )

    revenue = float(revenue_result.scalar() or 0)

    orders_result = await session.execute(
        select(
            func.count(Order.id)
        ).where(
            Order.status == "completed"
        )
    )

    orders = int(orders_result.scalar() or 0)

    average_order_value = (
        revenue / orders
        if orders > 0
        else 0
    )

    # ============================================================
    # CHECKOUT METRICS
    # ============================================================

    checkout_sessions_result = await session.execute(
        select(
            func.count(CheckoutSession.id)
        )
    )

    checkout_sessions = int(
        checkout_sessions_result.scalar() or 0
    )

    completed_checkout_result = await session.execute(
        select(
            func.count(CheckoutSession.id)
        ).where(
            CheckoutSession.status == "completed"
        )
    )

    completed_checkout = int(
        completed_checkout_result.scalar() or 0
    )

    abandoned_checkout_result = await session.execute(
        select(
            func.count(CheckoutSession.id)
        ).where(
            CheckoutSession.status == "abandoned"
        )
    )

    abandoned_checkout = int(
        abandoned_checkout_result.scalar() or 0
    )

    failed_checkout_result = await session.execute(
        select(
            func.count(CheckoutSession.id)
        ).where(
            CheckoutSession.status == "failed"
        )
    )

    failed_checkout = int(
        failed_checkout_result.scalar() or 0
    )

    completion_rate = (
        completed_checkout / checkout_sessions * 100
        if checkout_sessions > 0
        else 0
    )

    abandonment_rate = (
        abandoned_checkout / checkout_sessions * 100
        if checkout_sessions > 0
        else 0
    )

    checkout_failure_rate = (
        failed_checkout / checkout_sessions * 100
        if checkout_sessions > 0
        else 0
    )

    # ============================================================
    # PAYMENT METRICS
    # ============================================================

    payment_attempts_result = await session.execute(
        select(
            func.count(Payment.id)
        )
    )

    payment_attempts = int(
        payment_attempts_result.scalar() or 0
    )

    successful_payments_result = await session.execute(
        select(
            func.count(Payment.id)
        ).where(
            Payment.status == "success"
        )
    )

    successful_payments = int(
        successful_payments_result.scalar() or 0
    )

    failed_payments_result = await session.execute(
        select(
            func.count(Payment.id)
        ).where(
            Payment.status == "failed"
        )
    )

    failed_payments = int(
        failed_payments_result.scalar() or 0
    )

    payment_success_rate = (
        successful_payments / payment_attempts * 100
        if payment_attempts > 0
        else 0
    )

    payment_failure_rate = (
        failed_payments / payment_attempts * 100
        if payment_attempts > 0
        else 0
    )

    # ============================================================
    # DEVICE PERFORMANCE
    # ============================================================

    device_result = await session.execute(
        select(
            CheckoutSession.device_type,
            func.count(CheckoutSession.id)
        ).group_by(
            CheckoutSession.device_type
        )
    )

    device_rows = device_result.all()

    device_performance = {}

    for device_type, total_sessions in device_rows:

        completed_result = await session.execute(
            select(
                func.count(CheckoutSession.id)
            ).where(
                CheckoutSession.device_type == device_type,
                CheckoutSession.status == "completed"
            )
        )

        completed = int(
            completed_result.scalar() or 0
        )

        abandoned_result = await session.execute(
            select(
                func.count(CheckoutSession.id)
            ).where(
                CheckoutSession.device_type == device_type,
                CheckoutSession.status == "abandoned"
            )
        )

        abandoned = int(
            abandoned_result.scalar() or 0
        )

        failed_result = await session.execute(
            select(
                func.count(CheckoutSession.id)
            ).where(
                CheckoutSession.device_type == device_type,
                CheckoutSession.status == "failed"
            )
        )

        failed = int(
            failed_result.scalar() or 0
        )

        payment_attempts_result = await session.execute(
            select(
                func.count(Payment.id)
            )
            .join(
                CheckoutSession,
                Payment.checkout_session_id
                == CheckoutSession.id
            )
            .where(
                CheckoutSession.device_type == device_type
            )
        )

        device_payment_attempts = int(
            payment_attempts_result.scalar() or 0
        )

        successful_device_payments_result = await session.execute(
            select(
                func.count(Payment.id)
            )
            .join(
                CheckoutSession,
                Payment.checkout_session_id
                == CheckoutSession.id
            )
            .where(
                CheckoutSession.device_type == device_type,
                Payment.status == "success"
            )
        )

        successful_device_payments = int(
            successful_device_payments_result.scalar() or 0
        )

        conversion_rate = (
            completed / total_sessions * 100
            if total_sessions > 0
            else 0
        )

        abandonment_rate_device = (
            abandoned / total_sessions * 100
            if total_sessions > 0
            else 0
        )

        failure_rate_device = (
            failed / total_sessions * 100
            if total_sessions > 0
            else 0
        )

        payment_success_rate_device = (
            successful_device_payments
            / device_payment_attempts
            * 100
            if device_payment_attempts > 0
            else 0
        )

        device_performance[device_type] = {
            "checkout_sessions": int(total_sessions),
            "completed": completed,
            "abandoned": abandoned,
            "failed": failed,
            "conversion_rate": round(
                conversion_rate,
                2
            ),
            "abandonment_rate": round(
                abandonment_rate_device,
                2
            ),
            "failure_rate": round(
                failure_rate_device,
                2
            ),
            "payment_attempts": device_payment_attempts,
            "payment_success_rate": round(
                payment_success_rate_device,
                2
            ),
        }

    # ============================================================
    # PAYMENT METHOD PERFORMANCE
    # ============================================================

    payment_method_result = await session.execute(
        select(
            Payment.payment_method,
            func.count(Payment.id)
        ).group_by(
            Payment.payment_method
        )
    )

    payment_method_rows = payment_method_result.all()

    payment_method_performance = {}

    for payment_method, attempts in payment_method_rows:

        successful_result = await session.execute(
            select(
                func.count(Payment.id)
            ).where(
                Payment.payment_method == payment_method,
                Payment.status == "success"
            )
        )

        successful = int(
            successful_result.scalar() or 0
        )

        failed_result = await session.execute(
            select(
                func.count(Payment.id)
            ).where(
                Payment.payment_method == payment_method,
                Payment.status == "failed"
            )
        )

        failed = int(
            failed_result.scalar() or 0
        )

        success_rate = (
            successful / attempts * 100
            if attempts > 0
            else 0
        )

        failure_rate = (
            failed / attempts * 100
            if attempts > 0
            else 0
        )

        payment_method_performance[payment_method] = {
            "payment_attempts": int(attempts),
            "successful": successful,
            "failed": failed,
            "success_rate": round(
                success_rate,
                2
            ),
            "failure_rate": round(
                failure_rate,
                2
            ),
        }

    # ============================================================
    # PRODUCT PERFORMANCE
    # ============================================================

    product_result = await session.execute(
        select(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            Product.cost,
            Product.inventory,
            Product.views,

            func.coalesce(
                func.sum(OrderItem.quantity),
                0
            ).label("units_sold"),

            func.count(
                func.distinct(OrderItem.order_id)
            ).label(
                "orders_containing_product"
            )

        )
        .select_from(Product)
        .join(
            OrderItem,
            Product.id == OrderItem.product_id,
            isouter=True
        )
        .join(
            Order,
            Order.id == OrderItem.order_id,
            isouter=True
        )
        .where(
            (Order.id == None)
            | (Order.status == "completed")
        )
        .group_by(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            Product.cost,
            Product.inventory,
            Product.views
        )
    )

    product_rows = product_result.all()

    product_performance = []

    for row in product_rows:

        product_id = row[0]
        product_name = row[1]
        category = row[2]
        price = float(row[3] or 0)
        cost = float(row[4] or 0)
        inventory = int(row[5] or 0)
        views = int(row[6] or 0)
        units_sold = int(row[7] or 0)
        orders_containing_product = int(row[8] or 0)

        product_revenue = units_sold * price

        product_profit = (
            units_sold * (price - cost)
        )

        margin_percent = (
            (price - cost) / price * 100
            if price > 0
            else 0
        )

        conversion_rate = (
            orders_containing_product
            / views
            * 100
            if views > 0
            else 0
        )

        # IMPORTANT:
        # These names match offer_agent.py.
        product_performance.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "price": price,
            "cost": cost,
            "inventory": inventory,
            "views": views,
            "units_sold": units_sold,
            "orders_containing_product": (
                orders_containing_product
            ),
            "revenue": round(
                product_revenue,
                2
            ),
            "profit": round(
                product_profit,
                2
            ),
            "margin_percent": round(
                margin_percent,
                2
            ),
            "conversion_rate": round(
                conversion_rate,
                2
            ),
        })

    # ============================================================
    # FINAL ANALYTICS RESPONSE
    # ============================================================

    return {
        "business": {
            "revenue": round(revenue, 2),
            "orders": orders,
            "average_order_value": round(
                average_order_value,
                2
            ),
        },

        "checkout": {
            "sessions": checkout_sessions,
            "completed": completed_checkout,
            "abandoned": abandoned_checkout,
            "failed": failed_checkout,
            "completion_rate": round(
                completion_rate,
                2
            ),
            "abandonment_rate": round(
                abandonment_rate,
                2
            ),
            "failure_rate": round(
                checkout_failure_rate,
                2
            ),
        },

        "payments": {
            "attempts": payment_attempts,
            "successful": successful_payments,
            "failed": failed_payments,
            "success_rate": round(
                payment_success_rate,
                2
            ),
            "failure_rate": round(
                payment_failure_rate,
                2
            ),
        },

        "device_performance": device_performance,

        "payment_method_performance": (
            payment_method_performance
        ),

        "product_performance": product_performance,
    }