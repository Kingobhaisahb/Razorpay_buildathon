import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine
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


# ==========================================
# CONFIGURATION
# ==========================================

random.seed(42)

NUM_PRODUCTS = 100
NUM_CUSTOMERS = 1000
NUM_ORDERS = 5000
NUM_CHECKOUTS = 10000


# ==========================================
# SAMPLE DATA
# ==========================================

PRODUCT_CATEGORIES = [
    "Electronics",
    "Fashion",
    "Home",
    "Beauty",
    "Sports",
    "Accessories",
]

PRODUCT_NAMES = [
    "Smart Watch",
    "Wireless Earbuds",
    "Running Shoes",
    "Bluetooth Speaker",
    "Laptop Backpack",
    "Fitness Band",
    "Phone Case",
    "Travel Bag",
    "Cotton Hoodie",
    "Sports Jacket",
    "Desk Lamp",
    "Water Bottle",
    "Yoga Mat",
    "Mechanical Keyboard",
    "Wireless Mouse",
]


# ==========================================
# MAIN SEED FUNCTION
# ==========================================

async def seed_database():

    async with AsyncSession(engine) as session:

        print("Clearing existing data...")

        # Delete in dependency order
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

        print("Existing data cleared.")

        # ==========================================
        # MERCHANT
        # ==========================================

        merchant = Merchant(
            name="NovaCart",
            email="merchant@novacart.demo",
            created_at=datetime.utcnow()
        )

        session.add(merchant)
        await session.flush()

        print("Created merchant.")

        # ==========================================
        # PRODUCTS
        # ==========================================

        products = []

        for i in range(NUM_PRODUCTS):

            category = random.choice(PRODUCT_CATEGORIES)

            base_price = random.choice([
                499,
                799,
                999,
                1499,
                1999,
                2499,
                2999,
                3999,
                4999,
                6999,
            ])

            # Product cost is between 45% and 80% of selling price
            cost = round(
                base_price * random.uniform(0.45, 0.80),
                2
            )

            inventory = random.randint(10, 500)
            views = random.randint(500, 5000)

            if i in [7, 19, 34, 58, 81]:
                views = random.randint(7000, 12000)

            product = Product(
                merchant_id=merchant.id,
                name=f"{random.choice(PRODUCT_NAMES)} {i + 1}",
                category=category,
                price=base_price,
                cost=cost,
                inventory=inventory,
                views=views,
                created_at=datetime.utcnow()
            )

            products.append(product)

        session.add_all(products)
        await session.flush()

        print(f"Created {len(products)} products.")

        # ==========================================
        # CUSTOMERS
        # ==========================================

        customers = []

        devices = ["mobile", "desktop", "tablet"]

        for i in range(NUM_CUSTOMERS):

            customer = Customer(
                merchant_id=merchant.id,
                name=f"Customer {i + 1}",
                email=f"customer{i + 1}@example.com",
                device_type=random.choices(
                    devices,
                    weights=[65, 30, 5]
                )[0],
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(1, 365)
                )
            )

            customers.append(customer)

        session.add_all(customers)
        await session.flush()

        print(f"Created {len(customers)} customers.")

        # ==========================================
        # ORDERS + ORDER ITEMS
        # ==========================================

        orders = []
        order_items = []

        for i in range(NUM_ORDERS):

            customer = random.choice(customers)
            product = random.choice(products)

            quantity = random.choices(
                [1, 2, 3],
                weights=[75, 20, 5]
            )[0]

            amount = round(
                product.price * quantity,
                2
            )

            order = Order(
                merchant_id=merchant.id,
                customer_id=customer.id,
                total_amount=amount,
                status="completed",
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(1, 180)
                )
            )

            orders.append(order)

            order_item = OrderItem(
                order_id=0,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )

            order_items.append((order, order_item))

        session.add_all(orders)
        await session.flush()

        for order, item in order_items:
            item.order_id = order.id

        session.add_all(
            [item for _, item in order_items]
        )

        print(f"Created {len(orders)} orders.")

        # ==========================================
        # CHECKOUT SESSIONS + PAYMENTS
        # ==========================================

        checkouts = []
        payments = []

        payment_methods = [
            "upi",
            "card",
            "netbanking",
            "wallet",
        ]

        for i in range(NUM_CHECKOUTS):

            customer = random.choice(customers)

            device = customer.device_type

            payment_method = random.choices(
                payment_methods,
                weights=[55, 30, 10, 5]
            )[0]

            cart_value = round(
                random.uniform(500, 7000),
                2
            )

            # --------------------------------------
            # Introduce realistic checkout behavior
            # --------------------------------------

            # Mobile + UPI intentionally performs worse
            if device == "mobile" and payment_method == "upi":

                status = random.choices(
                    ["completed", "abandoned", "failed"],
                    weights=[55, 25, 20]
                )[0]

            else:

                status = random.choices(
                    ["completed", "abandoned", "failed"],
                    weights=[75, 15, 10]
                )[0]

            checkout = CheckoutSession(
                merchant_id=merchant.id,
                customer_id=customer.id,
                device_type=device,
                payment_method=payment_method,
                cart_value=cart_value,
                status=status,
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(1, 90)
                )
            )

            checkouts.append(checkout)

        session.add_all(checkouts)
        await session.flush()

        print(f"Created {len(checkouts)} checkout sessions.")

        # ==========================================
        # PAYMENTS
        # ==========================================

        for checkout in checkouts:

            # Abandoned checkout may never reach payment
            if checkout.status == "abandoned":
                continue

            if checkout.status == "completed":

                payment_status = "success"
                failure_reason = None

            else:

                payment_status = "failed"

                failure_reason = random.choice([
                    "bank_declined",
                    "insufficient_funds",
                    "timeout",
                    "technical_error",
                ])

            payment = Payment(
                checkout_session_id=checkout.id,
                amount=checkout.cart_value,
                payment_method=checkout.payment_method,
                status=payment_status,
                failure_reason=failure_reason,
                created_at=checkout.created_at
            )

            payments.append(payment)

        session.add_all(payments)

        print(f"Created {len(payments)} payments.")

        # ==========================================
        # OFFERS
        # ==========================================

        offers = [

            Offer(
                merchant_id=merchant.id,
                name="Summer Sale",
                discount_percent=10,
                max_discount_percent=15,
                min_margin_percent=25,
                budget=50000,
                active=True
            ),

            Offer(
                merchant_id=merchant.id,
                name="New Customer Offer",
                discount_percent=5,
                max_discount_percent=10,
                min_margin_percent=30,
                budget=25000,
                active=True
            ),

            Offer(
                merchant_id=merchant.id,
                name="Weekend Flash Sale",
                discount_percent=15,
                max_discount_percent=15,
                min_margin_percent=20,
                budget=15000,
                active=False
            ),
        ]

        session.add_all(offers)

        print("Created offers.")

        # ==========================================
        # EXPERIMENTS
        # ==========================================

        experiments = [

            Experiment(
                merchant_id=merchant.id,
                name="Mobile Checkout Test",
                hypothesis="Simplifying mobile checkout will increase conversion.",
                control_conversion=64.2,
                variant_conversion=77.8,
                status="completed",
                winner="variant"
            ),

            Experiment(
                merchant_id=merchant.id,
                name="Free Shipping Banner",
                hypothesis="Showing free shipping earlier will reduce checkout abandonment.",
                control_conversion=68.4,
                variant_conversion=69.1,
                status="completed",
                winner="variant"
            ),

            Experiment(
                merchant_id=merchant.id,
                name="Product Recommendation Test",
                hypothesis="Showing related products will increase average order value.",
                control_conversion=72.5,
                variant_conversion=71.8,
                status="completed",
                winner="control"
            ),
        ]

        session.add_all(experiments)

        print("Created experiments.")

        # ==========================================
        # AI ACTION HISTORY
        # ==========================================

        ai_actions = [

            AIAction(
                merchant_id=merchant.id,
                agent_name="Checkout Agent",
                action_type="detect_issue",
                description="Detected elevated mobile checkout abandonment.",
                status="completed",
                expected_impact=8.5,
                actual_impact=6.2
            ),

            AIAction(
                merchant_id=merchant.id,
                agent_name="A/B Testing Agent",
                action_type="create_experiment",
                description="Created mobile checkout optimization experiment.",
                status="completed",
                expected_impact=12.0,
                actual_impact=13.6
            ),

            AIAction(
                merchant_id=merchant.id,
                agent_name="Offer Agent",
                action_type="create_offer",
                description="Proposed targeted discount for high-intent customers.",
                status="pending",
                expected_impact=7.5,
                actual_impact=0.0
            ),
        ]

        session.add_all(ai_actions)

        print("Created AI action history.")

        # ==========================================
        # COMMIT EVERYTHING
        # ==========================================

        await session.commit()

        print()
        print("======================================")
        print("ShopControl database seeded successfully!")
        print("======================================")
        print(f"Merchant:          1")
        print(f"Products:          {NUM_PRODUCTS}")
        print(f"Customers:         {NUM_CUSTOMERS}")
        print(f"Orders:            {NUM_ORDERS}")
        print(f"Checkout Sessions: {NUM_CHECKOUTS}")
        print(f"Payments:          {len(payments)}")
        print(f"Offers:            {len(offers)}")
        print(f"Experiments:       {len(experiments)}")
        print(f"AI Actions:        {len(ai_actions)}")


# ==========================================
# RUN SCRIPT
# ==========================================

if __name__ == "__main__":
    asyncio.run(seed_database())