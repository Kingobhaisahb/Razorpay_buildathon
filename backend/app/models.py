from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    name: Mapped[str] = mapped_column(
        String(150)
    )

    category: Mapped[str] = mapped_column(
        String(100)
    )

    price: Mapped[float] = mapped_column(
        Float
    )

    cost: Mapped[float] = mapped_column(
        Float
    )

    inventory: Mapped[int] = mapped_column(
        Integer
    )

    views: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    email: Mapped[str] = mapped_column(
        String(150)
    )

    device_type: Mapped[str] = mapped_column(
        String(50)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    total_amount: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    price: Mapped[float] = mapped_column(
        Float
    )


class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )

    device_type: Mapped[str] = mapped_column(
        String(50)
    )

    payment_method: Mapped[str] = mapped_column(
        String(50)
    )

    cart_value: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    checkout_session_id: Mapped[int] = mapped_column(
        ForeignKey("checkout_sessions.id")
    )

    amount: Mapped[float] = mapped_column(
        Float
    )

    payment_method: Mapped[str] = mapped_column(
        String(50)
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    failure_reason: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    name: Mapped[str] = mapped_column(
        String(150)
    )

    discount_percent: Mapped[float] = mapped_column(
        Float
    )

    max_discount_percent: Mapped[float] = mapped_column(
        Float
    )

    min_margin_percent: Mapped[float] = mapped_column(
        Float
    )

    budget: Mapped[float] = mapped_column(
        Float
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    name: Mapped[str] = mapped_column(
        String(150)
    )

    hypothesis: Mapped[str] = mapped_column(
        String(500)
    )

    # -----------------------------
    # Sample sizes
    # -----------------------------

    control_visitors: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    variant_visitors: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # -----------------------------
    # Conversions
    # -----------------------------

    control_conversions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    variant_conversions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    # -----------------------------
    # Conversion rates
    # -----------------------------

    control_conversion: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    variant_conversion: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    # -----------------------------
    # Revenue
    # -----------------------------

    control_revenue: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    variant_revenue: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    # -----------------------------
    # Experiment analysis
    # -----------------------------

    conversion_lift: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    revenue_lift: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    p_value: Mapped[float] = mapped_column(
        Float,
        default=1.0
    )

    statistically_significant: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # -----------------------------
    # Status / decision
    # -----------------------------

    status: Mapped[str] = mapped_column(
        String(50)
    )

    winner: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class AIAction(Base):
    __tablename__ = "ai_actions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    agent_name: Mapped[str] = mapped_column(
        String(100)
    )

    action_type: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str] = mapped_column(
        String(500)
    )

    status: Mapped[str] = mapped_column(
        String(50)
    )

    expected_impact: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    actual_impact: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )