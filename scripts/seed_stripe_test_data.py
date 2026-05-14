"""Create realistic Stripe test-mode data for local pipeline development."""

from __future__ import annotations

import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse import config, stripe_client

import stripe


SEED_BATCH_ID = f"portfolio_seed_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

CUSTOMERS = [
    ("Ana Martins", "ana.martins@example.com", "BR"),
    ("Bruno Costa", "bruno.costa@example.com", "BR"),
    ("Carla Ribeiro", "carla.ribeiro@example.com", "BR"),
    ("Diego Santos", "diego.santos@example.com", "BR"),
    ("Eva Almeida", "eva.almeida@example.com", "PT"),
    ("Felipe Rocha", "felipe.rocha@example.com", "BR"),
    ("Giulia Nunes", "giulia.nunes@example.com", "IT"),
    ("Hugo Pereira", "hugo.pereira@example.com", "PT"),
    ("Isabela Lima", "isabela.lima@example.com", "BR"),
    ("Joao Ferreira", "joao.ferreira@example.com", "BR"),
    ("Karin Muller", "karin.muller@example.com", "DE"),
    ("Lucas Araujo", "lucas.araujo@example.com", "BR"),
    ("Marina Souza", "marina.souza@example.com", "BR"),
    ("Nicolas Weber", "nicolas.weber@example.com", "DE"),
    ("Olivia Rossi", "olivia.rossi@example.com", "IT"),
    ("Paulo Gomes", "paulo.gomes@example.com", "BR"),
    ("Renata Alves", "renata.alves@example.com", "BR"),
    ("Sofia Carvalho", "sofia.carvalho@example.com", "PT"),
    ("Thiago Moreira", "thiago.moreira@example.com", "BR"),
    ("Valentina Bianchi", "valentina.bianchi@example.com", "IT"),
    ("William Johnson", "william.johnson@example.com", "US"),
    ("Ximena Torres", "ximena.torres@example.com", "MX"),
    ("Yara Oliveira", "yara.oliveira@example.com", "BR"),
    ("Zoe Miller", "zoe.miller@example.com", "US"),
]

SUCCESSFUL_PAYMENTS = [
    ("usd", 2500, "starter_subscription"),
    ("usd", 4990, "starter_subscription"),
    ("usd", 12000, "annual_subscription"),
    ("usd", 1550, "one_time_addon"),
    ("usd", 8800, "professional_subscription"),
    ("usd", 3400, "usage_invoice"),
    ("usd", 1999, "one_time_addon"),
    ("usd", 21000, "enterprise_invoice"),
    ("brl", 7990, "starter_subscription"),
    ("brl", 15000, "professional_subscription"),
    ("brl", 29900, "annual_subscription"),
    ("brl", 3500, "one_time_addon"),
    ("brl", 4590, "usage_invoice"),
    ("brl", 9900, "starter_subscription"),
    ("brl", 18750, "professional_subscription"),
    ("brl", 42000, "enterprise_invoice"),
    ("eur", 4200, "starter_subscription"),
    ("eur", 8800, "professional_subscription"),
    ("eur", 1999, "one_time_addon"),
    ("eur", 21000, "annual_subscription"),
    ("eur", 6750, "usage_invoice"),
    ("eur", 3300, "one_time_addon"),
    ("eur", 14200, "professional_subscription"),
    ("eur", 26000, "enterprise_invoice"),
    ("gbp", 3200, "starter_subscription"),
    ("gbp", 7900, "professional_subscription"),
    ("gbp", 18500, "annual_subscription"),
    ("gbp", 1250, "one_time_addon"),
    ("mxn", 45000, "starter_subscription"),
    ("mxn", 120000, "professional_subscription"),
    ("mxn", 78000, "usage_invoice"),
    ("mxn", 250000, "annual_subscription"),
    ("cad", 5600, "starter_subscription"),
    ("cad", 11200, "professional_subscription"),
    ("cad", 24500, "annual_subscription"),
    ("cad", 3300, "one_time_addon"),
]

FAILED_PAYMENTS = [
    ("usd", 2900, "card_declined"),
    ("usd", 12900, "card_declined"),
    ("brl", 6500, "card_declined"),
    ("brl", 22000, "card_declined"),
    ("eur", 4700, "card_declined"),
    ("gbp", 9800, "card_declined"),
]


def main() -> None:
    load_dotenv()
    settings = config.load_settings()
    stripe_client.configure_stripe(settings.stripe_api_key)

    customers = create_customers()
    successful_payment_intents = create_successful_payments(customers)
    failed_payment_intents = create_failed_payments(customers)
    refunds = create_refunds(successful_payment_intents)

    print(f"Seed batch: {SEED_BATCH_ID}")
    print(f"Customers created: {len(customers)}")
    print(f"Successful payment intents created: {len(successful_payment_intents)}")
    print(f"Failed payment intents created: {len(failed_payment_intents)}")
    print(f"Refunds created: {len(refunds)}")


def create_customers() -> list[stripe.Customer]:
    customers = []

    for index, (name, email, country) in enumerate(CUSTOMERS, start=1):
        customer = stripe.Customer.create(
            name=name,
            email=email,
            metadata={
                "seed_batch_id": SEED_BATCH_ID,
                "customer_number": str(index),
                "country": country,
                "segment": customer_segment(index),
            },
        )
        customers.append(customer)

    return customers


def create_successful_payments(customers: list[stripe.Customer]) -> list[stripe.PaymentIntent]:
    payment_intents = []

    for index, (currency, amount, product_family) in enumerate(SUCCESSFUL_PAYMENTS, start=1):
        customer = customers[(index - 1) % len(customers)]
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer.id,
            payment_method="pm_card_visa",
            confirm=True,
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never",
            },
            metadata={
                "seed_batch_id": SEED_BATCH_ID,
                "payment_number": str(index),
                "product_family": product_family,
                "scenario": "successful_payment",
            },
        )
        payment_intents.append(payment_intent)

    return payment_intents


def create_failed_payments(customers: list[stripe.Customer]) -> list[stripe.PaymentIntent]:
    payment_intents = []

    for index, (currency, amount, reason) in enumerate(FAILED_PAYMENTS, start=1):
        customer = customers[-index]
        try:
            stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer.id,
                payment_method="pm_card_chargeDeclined",
                confirm=True,
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never",
                },
                metadata={
                    "seed_batch_id": SEED_BATCH_ID,
                    "payment_number": str(index),
                    "scenario": "failed_payment",
                    "failure_reason": reason,
                },
            )
        except stripe.error.CardError as error:
            payment_intent = error.json_body.get("error", {}).get("payment_intent")
            if payment_intent:
                payment_intents.append(payment_intent)

    return payment_intents


def create_refunds(payment_intents: list[stripe.PaymentIntent]) -> list[stripe.Refund]:
    refunds = []
    refundable_payment_intents = random.sample(payment_intents, k=6)

    for index, payment_intent in enumerate(refundable_payment_intents, start=1):
        charge_id = payment_intent.latest_charge
        if not charge_id:
            continue

        refund_amount = int(payment_intent.amount * 0.5) if index % 2 == 0 else None
        refund_params = {
            "charge": charge_id,
            "metadata": {
                "seed_batch_id": SEED_BATCH_ID,
                "refund_number": str(index),
                "scenario": "seeded_refund",
            },
        }
        if refund_amount:
            refund_params["amount"] = refund_amount

        refunds.append(stripe.Refund.create(**refund_params))

    return refunds


def customer_segment(index: int) -> str:
    if index % 5 == 0:
        return "enterprise"
    if index % 3 == 0:
        return "professional"
    return "starter"


if __name__ == "__main__":
    main()
