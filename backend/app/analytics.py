from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Order,
    OrderItem,
    CheckoutSession,
    Payment,
    Product,
)


async def get_business_metrics(session: AsyncSession):

    # =====================================================
    # 1. OVERALL BUSINESS METRICS
    # =====================================================

    revenue_result = await session.execute(
        select(func.coalesce(func.sum(Order.total_amount), 0))
        .where(Order.status == "completed")
    )

    total_revenue = float(revenue_result.scalar_one())

    orders_result = await session.execute(
        select(func.count(Order.id))
        .where(Order.status == "completed")
    )

    total_orders = orders_result.scalar_one()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # =====================================================
    # 2. CHECKOUT METRICS
    # =====================================================

    checkout_result = await session.execute(
        select(func.count(CheckoutSession.id))
    )

    total_checkouts = checkout_result.scalar_one()

    completed_result = await session.execute(
        select(func.count(CheckoutSession.id))
        .where(CheckoutSession.status == "completed")
    )

    completed_checkouts = completed_result.scalar_one()

    abandoned_result = await session.execute(
        select(func.count(CheckoutSession.id))
        .where(CheckoutSession.status == "abandoned")
    )

    abandoned_checkouts = abandoned_result.scalar_one()

    failed_result = await session.execute(
        select(func.count(CheckoutSession.id))
        .where(CheckoutSession.status == "failed")
    )

    failed_checkouts = failed_result.scalar_one()

    checkout_completion_rate = (
        completed_checkouts / total_checkouts * 100
        if total_checkouts > 0
        else 0
    )

    checkout_abandonment_rate = (
        abandoned_checkouts / total_checkouts * 100
        if total_checkouts > 0
        else 0
    )

    checkout_failure_rate = (
        failed_checkouts / total_checkouts * 100
        if total_checkouts > 0
        else 0
    )

    # =====================================================
    # 3. PAYMENT METRICS
    # =====================================================

    total_payments_result = await session.execute(
        select(func.count(Payment.id))
    )

    total_payments = total_payments_result.scalar_one()

    successful_payments_result = await session.execute(
        select(func.count(Payment.id))
        .where(Payment.status == "success")
    )

    successful_payments = successful_payments_result.scalar_one()

    failed_payments_result = await session.execute(
        select(func.count(Payment.id))
        .where(Payment.status == "failed")
    )

    failed_payments = failed_payments_result.scalar_one()

    payment_success_rate = (
        successful_payments / total_payments * 100
        if total_payments > 0
        else 0
    )

    payment_failure_rate = (
        failed_payments / total_payments * 100
        if total_payments > 0
        else 0
    )

    # =====================================================
    # 4. DEVICE PERFORMANCE
    # =====================================================

    device_result = await session.execute(
        select(
            CheckoutSession.device_type,
            func.count(CheckoutSession.id)
        )
        .group_by(CheckoutSession.device_type)
    )

    device_rows = device_result.all()

    device_performance = {}

    for device, total in device_rows:

        completed_result = await session.execute(
            select(func.count(CheckoutSession.id))
            .where(
                CheckoutSession.device_type == device,
                CheckoutSession.status == "completed"
            )
        )

        completed = completed_result.scalar_one()

        abandoned_result = await session.execute(
            select(func.count(CheckoutSession.id))
            .where(
                CheckoutSession.device_type == device,
                CheckoutSession.status == "abandoned"
            )
        )

        abandoned = abandoned_result.scalar_one()

        failed_result = await session.execute(
            select(func.count(CheckoutSession.id))
            .where(
                CheckoutSession.device_type == device,
                CheckoutSession.status == "failed"
            )
        )

        failed = failed_result.scalar_one()

        payment_attempt_result = await session.execute(
            select(func.count(Payment.id))
            .join(
                CheckoutSession,
                Payment.checkout_session_id == CheckoutSession.id
            )
            .where(
                CheckoutSession.device_type == device
            )
        )

        payment_attempts = payment_attempt_result.scalar_one()

        successful_payment_result = await session.execute(
            select(func.count(Payment.id))
            .join(
                CheckoutSession,
                Payment.checkout_session_id == CheckoutSession.id
            )
            .where(
                CheckoutSession.device_type == device,
                Payment.status == "success"
            )
        )

        successful_device_payments = (
            successful_payment_result.scalar_one()
        )

        device_performance[device] = {
            "checkout_sessions": total,
            "completed": completed,
            "abandoned": abandoned,
            "failed": failed,
            "conversion_rate": round(
                completed / total * 100,
                2
            ) if total > 0 else 0,
            "abandonment_rate": round(
                abandoned / total * 100,
                2
            ) if total > 0 else 0,
            "failure_rate": round(
                failed / total * 100,
                2
            ) if total > 0 else 0,
            "payment_attempts": payment_attempts,
            "payment_success_rate": round(
                successful_device_payments / payment_attempts * 100,
                2
            ) if payment_attempts > 0 else 0
        }

    # =====================================================
    # 5. PAYMENT METHOD PERFORMANCE
    # =====================================================

    payment_method_result = await session.execute(
        select(
            Payment.payment_method,
            func.count(Payment.id)
        )
        .group_by(Payment.payment_method)
    )

    payment_method_rows = payment_method_result.all()

    payment_method_performance = {}

    for method, total in payment_method_rows:

        success_result = await session.execute(
            select(func.count(Payment.id))
            .where(
                Payment.payment_method == method,
                Payment.status == "success"
            )
        )

        successful = success_result.scalar_one()

        failed_result = await session.execute(
            select(func.count(Payment.id))
            .where(
                Payment.payment_method == method,
                Payment.status == "failed"
            )
        )

        failed = failed_result.scalar_one()

        payment_method_performance[method] = {
            "payment_attempts": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(
                successful / total * 100,
                2
            ) if total > 0 else 0,
            "failure_rate": round(
                failed / total * 100,
                2
            ) if total > 0 else 0
        }

    # =====================================================
    # 6. PRODUCT PERFORMANCE
    # =====================================================

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
            ).label("orders_containing_product")
        )
        .outerjoin(
            OrderItem,
            Product.id == OrderItem.product_id
        )
        .outerjoin(
            Order,
            Order.id == OrderItem.order_id
        )
        .where(
            (Order.id.is_(None)) | (Order.status == "completed")
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

        units_sold = int(row.units_sold)

        revenue = round(
            units_sold * row.price,
            2
        )

        profit = round(
            units_sold * (row.price - row.cost),
            2
        )

        margin_percent = round(
            (row.price - row.cost) / row.price * 100,
            2
        ) if row.price > 0 else 0

        conversion_rate = round(
            row.orders_containing_product / row.views * 100,
            2
        ) if row.views > 0 else 0

        product_performance.append({
            "product_id": row.id,
            "name": row.name,
            "category": row.category,
            "price": row.price,
            "cost": row.cost,
            "inventory": row.inventory,
            "views": row.views,
            "units_sold": units_sold,
            "orders_containing_product": row.orders_containing_product,
            "conversion_rate": conversion_rate,
            "revenue": revenue,
            "profit": profit,
            "margin_percent": margin_percent
        })

    # =====================================================
    # 7. RETURN EVERYTHING
    # =====================================================

    return {
        "business": {
            "revenue": round(total_revenue, 2),
            "orders": total_orders,
            "average_order_value": round(
                average_order_value,
                2
            )
        },

        "checkout": {
            "sessions": total_checkouts,
            "completed": completed_checkouts,
            "abandoned": abandoned_checkouts,
            "failed": failed_checkouts,
            "completion_rate": round(
                checkout_completion_rate,
                2
            ),
            "abandonment_rate": round(
                checkout_abandonment_rate,
                2
            ),
            "failure_rate": round(
                checkout_failure_rate,
                2
            )
        },

        "payments": {
            "attempts": total_payments,
            "successful": successful_payments,
            "failed": failed_payments,
            "success_rate": round(
                payment_success_rate,
                2
            ),
            "failure_rate": round(
                payment_failure_rate,
                2
            )
        },

        "device_performance": device_performance,

        "payment_method_performance": payment_method_performance,

        "product_performance": product_performance
    }