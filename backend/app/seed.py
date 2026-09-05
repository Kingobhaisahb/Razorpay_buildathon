import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import delete

from .database import engine, AsyncSessionLocal, Base
from .models import (
    Merchant,
    Product,
    Customer,
    Order,
    OrderItem,
    CheckoutSession,
    Payment,
    Offer,
    Experiment,
    AIAction,
)


# ============================================================
# CONFIG
# ============================================================

random.seed(42)

MERCHANT_ID = 1


# ============================================================
# CREATE TABLES
# ============================================================

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


# ============================================================
# SEED DATABASE
# ============================================================

async def seed_database():

    # Create tables first.
    # This allows the seed script to work even if
    # shopcontrol.db was deleted.

    await create_tables()

    print("Clearing existing data...")

    async with AsyncSessionLocal() as session:

        # ====================================================
        # CLEAR EXISTING DATA
        # ====================================================

        await session.execute(delete(AIAction))
        await session.execute(delete(Experiment))
        await session.execute(delete(Offer))
        await session.execute(delete(Payment))
        await session.execute(delete(CheckoutSession))
        await session.execute(delete(OrderItem))
        await session.execute(delete(Order))
        await session.execute(delete(Customer))
        await session.execute(delete(Product))
        await session.execute(delete(Merchant))

        await session.commit()

        # ====================================================
        # MERCHANT
        # ====================================================

        merchant = Merchant(
            id=MERCHANT_ID,
            name="Demo Merchant",
            email="merchant@shopcontrol.ai",
        )

        session.add(merchant)

        await session.flush()

        # ====================================================
        # PRODUCTS
        # ====================================================

        print("Creating products...")

        categories = [
            "Electronics",
            "Fashion",
            "Home",
            "Beauty",
            "Sports",
            "Accessories",
        ]

        products = []

        for i in range(1, 101):

            category = random.choice(categories)

            price = round(
                random.uniform(500, 10000),
                2,
            )

            cost_percentage = random.uniform(
                0.45,
                0.75,
            )

            cost = round(
                price * cost_percentage,
                2,
            )

            inventory = random.randint(
                5,
                100,
            )

            views = random.randint(
                500,
                5000,
            )

            # High-traffic products.
            # These give the Offer Agent useful
            # opportunities to discover.

            if i in [7, 19, 34, 58, 81]:

                views = random.randint(
                    7000,
                    12000,
                )

            product = Product(
                merchant_id=MERCHANT_ID,
                name=f"{category} Product {i}",
                category=category,
                price=price,
                cost=cost,
                inventory=inventory,
                views=views,
            )

            products.append(product)

            session.add(product)

        # ----------------------------------------------------
        # SPECIAL OFFER-AGENT OPPORTUNITY
        # ----------------------------------------------------

        wireless_earbuds = Product(
            merchant_id=MERCHANT_ID,
            name="Wireless Earbuds 8",
            category="Electronics",
            price=6999.00,
            cost=3800.00,
            inventory=32,
            views=11392,
        )

        products.append(wireless_earbuds)

        session.add(wireless_earbuds)

        await session.flush()

        # ====================================================
        # CUSTOMERS
        # ====================================================

        print("Creating customers...")

        customers = []

        for i in range(1, 1001):

            customer = Customer(
                merchant_id=MERCHANT_ID,
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                device_type=random.choice(
                    [
                        "mobile",
                        "desktop",
                        "tablet",
                    ]
                ),
            )

            customers.append(customer)

            session.add(customer)

        await session.flush()

        # ====================================================
        # ORDERS
        # ====================================================

        print("Creating orders...")

        orders = []

        for i in range(1, 5001):

            customer = random.choice(
                customers
            )

            order_date = (
                datetime.utcnow()
                - timedelta(
                    days=random.randint(
                        0,
                        90,
                    )
                )
            )

            order = Order(
                merchant_id=MERCHANT_ID,
                customer_id=customer.id,
                total_amount=0,
                status="completed",
                created_at=order_date,
            )

            session.add(order)

            await session.flush()

            # ------------------------------------------------
            # ORDER ITEMS
            # ------------------------------------------------

            number_of_items = random.randint(
                1,
                4,
            )

            selected_products = random.sample(
                products,
                number_of_items,
            )

            order_total = 0

            for product in selected_products:

                quantity = random.randint(
                    1,
                    2,
                )

                item_price = product.price

                item_total = (
                    item_price * quantity
                )

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=item_price,
                )

                session.add(order_item)

                order_total += item_total

            order.total_amount = round(
                order_total,
                2,
            )

            orders.append(order)

        await session.flush()

        # ====================================================
        # CHECKOUT SESSIONS
        # ====================================================

        print("Creating checkout sessions...")

        devices = [
            "desktop",
            "mobile",
            "tablet",
        ]

        payment_methods = [
            "card",
            "upi",
            "netbanking",
            "wallet",
        ]

        checkout_sessions = []

        for i in range(10000):

            # ------------------------------------------------
            # DEVICE
            # ------------------------------------------------

            device = random.choices(
                devices,
                weights=[
                    28,
                    67,
                    5,
                ],
            )[0]

            # ------------------------------------------------
            # PAYMENT METHOD
            # ------------------------------------------------

            payment_method = random.choice(
                payment_methods
            )

            # ------------------------------------------------
            # CHECKOUT STATUS
            # ------------------------------------------------

            # Intentionally create weaker performance
            # for Mobile + UPI.
            #
            # This gives the Checkout Agent a genuine
            # data-driven opportunity to discover.

            if (
                device == "mobile"
                and payment_method == "upi"
            ):

                status = random.choices(
                    [
                        "completed",
                        "abandoned",
                        "failed",
                    ],
                    weights=[
                        55,
                        25,
                        20,
                    ],
                )[0]

            else:

                status = random.choices(
                    [
                        "completed",
                        "abandoned",
                        "failed",
                    ],
                    weights=[
                        75,
                        15,
                        10,
                    ],
                )[0]

            # ------------------------------------------------
            # CUSTOMER
            # ------------------------------------------------

            customer = random.choice(
                customers
            )

            # ------------------------------------------------
            # CART VALUE
            # ------------------------------------------------

            cart_value = round(
                random.uniform(
                    500,
                    15000,
                ),
                2,
            )

            # ------------------------------------------------
            # DATE
            # ------------------------------------------------

            session_date = (
                datetime.utcnow()
                - timedelta(
                    days=random.randint(
                        0,
                        90,
                    )
                )
            )

            # ------------------------------------------------
            # CREATE CHECKOUT
            # ------------------------------------------------

            checkout = CheckoutSession(
                merchant_id=MERCHANT_ID,
                customer_id=customer.id,
                device_type=device,
                payment_method=payment_method,
                cart_value=cart_value,
                status=status,
                created_at=session_date,
            )

            checkout_sessions.append(
                checkout
            )

            session.add(checkout)

        await session.flush()

        # ====================================================
        # PAYMENTS
        # ====================================================

        print("Creating payments...")

        payments = []

        for checkout in checkout_sessions:

            # ------------------------------------------------
            # ABANDONED CHECKOUTS
            # ------------------------------------------------

            if checkout.status == "abandoned":

                # Most abandoned sessions never attempt
                # payment.

                if random.random() > 0.15:
                    continue

            # ------------------------------------------------
            # PAYMENT STATUS
            # ------------------------------------------------

            if checkout.status == "completed":

                payment_status = "success"

                failure_reason = None

            else:

                payment_status = "failed"

                failure_reasons = [
                    "payment_timeout",
                    "bank_declined",
                    "gateway_error",
                    "user_cancelled",
                ]

                failure_reason = random.choice(
                    failure_reasons
                )

            # ------------------------------------------------
            # PAYMENT AMOUNT
            # ------------------------------------------------

            amount = checkout.cart_value

            # ------------------------------------------------
            # PAYMENT
            # ------------------------------------------------

            payment = Payment(
                checkout_session_id=checkout.id,
                amount=amount,
                payment_method=checkout.payment_method,
                status=payment_status,
                failure_reason=failure_reason,
                created_at=checkout.created_at,
            )

            payments.append(payment)

            session.add(payment)

        await session.flush()

        # ====================================================
        # OFFERS
        # ====================================================

        print("Creating offers...")

        offers = [
            Offer(
                merchant_id=MERCHANT_ID,
                name="Summer Electronics Sale",
                discount_percent=10.0,
                max_discount_percent=15.0,
                min_margin_percent=25.0,
                budget=50000.0,
                active=True,
            ),

            Offer(
                merchant_id=MERCHANT_ID,
                name="New Customer Offer",
                discount_percent=5.0,
                max_discount_percent=10.0,
                min_margin_percent=25.0,
                budget=30000.0,
                active=True,
            ),

            Offer(
                merchant_id=MERCHANT_ID,
                name="Weekend Special",
                discount_percent=15.0,
                max_discount_percent=15.0,
                min_margin_percent=25.0,
                budget=25000.0,
                active=False,
            ),
        ]

        session.add_all(offers)

        await session.flush()

        # ====================================================
        # EXPERIMENTS
        # ====================================================

        print("Creating experiments...")

        experiments = [

            # ------------------------------------------------
            # EXPERIMENT 1
            # ------------------------------------------------

            Experiment(
                merchant_id=MERCHANT_ID,
                name="Homepage CTA Test",
                hypothesis=(
                    "A stronger CTA will increase "
                    "checkout starts."
                ),

                control_visitors=2500,
                variant_visitors=2500,

                control_conversions=53,
                variant_conversions=61,

                control_conversion=2.10,
                variant_conversion=2.42,

                control_revenue=171000.0,
                variant_revenue=197000.0,

                conversion_lift=15.24,
                revenue_lift=15.20,

                p_value=0.41,
                statistically_significant=False,

                status="completed",
                winner="neutral",
            ),

            # ------------------------------------------------
            # EXPERIMENT 2
            # ------------------------------------------------

            Experiment(
                merchant_id=MERCHANT_ID,
                name="Product Page Offer Test",
                hypothesis=(
                    "Showing a targeted offer will "
                    "increase product conversion."
                ),

                control_visitors=3000,
                variant_visitors=3000,

                control_conversions=54,
                variant_conversions=65,

                control_conversion=1.80,
                variant_conversion=2.15,

                control_revenue=175000.0,
                variant_revenue=211000.0,

                conversion_lift=19.44,
                revenue_lift=20.57,

                p_value=0.04,
                statistically_significant=True,

                status="completed",
                winner="variant",
            ),

            # ------------------------------------------------
            # EXPERIMENT 3
            # ------------------------------------------------

            Experiment(
                merchant_id=MERCHANT_ID,
                name="Checkout Button Test",
                hypothesis=(
                    "Simplifying the checkout button "
                    "will improve conversion."
                ),

                control_visitors=2000,
                variant_visitors=2000,

                control_conversions=62,
                variant_conversions=58,

                control_conversion=3.10,
                variant_conversion=2.90,

                control_revenue=201000.0,
                variant_revenue=188000.0,

                conversion_lift=-6.45,
                revenue_lift=-6.47,

                p_value=0.61,
                statistically_significant=False,

                status="completed",
                winner="neutral",
            ),
        ]

        session.add_all(
            experiments
        )

        await session.flush()

        # ====================================================
        # AI ACTIONS
        # ====================================================

        print("Creating AI actions...")

        ai_actions = [

            # ------------------------------------------------
            # CHECKOUT AGENT
            # ------------------------------------------------

            AIAction(
                merchant_id=MERCHANT_ID,
                agent_name="Checkout Agent",
                action_type="optimization",
                description=(
                    "Detected lower UPI payment success "
                    "rates and recommended checkout "
                    "optimization."
                ),
                status="recommended",
                expected_impact=8.5,
                actual_impact=0.0,
            ),

            # ------------------------------------------------
            # OFFER AGENT
            # ------------------------------------------------

            AIAction(
                merchant_id=MERCHANT_ID,
                agent_name="Offer Agent",
                action_type="offer_creation",
                description=(
                    "Recommended a targeted 10% discount "
                    "for Wireless Earbuds 8."
                ),
                status="awaiting_approval",
                expected_impact=14.0,
                actual_impact=0.0,
            ),

            # ------------------------------------------------
            # A/B TESTING AGENT
            # ------------------------------------------------

            AIAction(
                merchant_id=MERCHANT_ID,
                agent_name="A/B Testing Agent",
                action_type="experiment",
                description=(
                    "Completed a controlled experiment "
                    "comparing the existing experience "
                    "against an optimized variant."
                ),
                status="completed",
                expected_impact=10.0,
                actual_impact=14.35,
            ),
        ]

        session.add_all(
            ai_actions
        )

        # ====================================================
        # COMMIT
        # ====================================================

        await session.commit()

        # ====================================================
        # FINAL OUTPUT
        # ====================================================

        print()
        print("=" * 60)
        print("        SHOPCONTROL DATABASE SEEDED")
        print("=" * 60)

        print(
            f"Merchant:          {MERCHANT_ID}"
        )

        print(
            f"Products:          {len(products)}"
        )

        print(
            f"Customers:         {len(customers)}"
        )

        print(
            f"Orders:            {len(orders)}"
        )

        print(
            f"Checkout Sessions: {len(checkout_sessions)}"
        )

        print(
            f"Payments:          {len(payments)}"
        )

        print(
            f"Offers:            {len(offers)}"
        )

        print(
            f"Experiments:       {len(experiments)}"
        )

        print(
            f"AI Actions:        {len(ai_actions)}"
        )

        print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(seed_database())