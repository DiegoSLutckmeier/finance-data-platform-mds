with payment_intents as (
    select *
    from {{ ref('stg_stripe_payment_intents') }}
),

charges as (
    select *
    from {{ ref('stg_stripe_charges') }}
),

joined as (
    select
        payment_intents.payment_intent_id,
        payment_intents.customer_id,
        payment_intents.latest_charge_id as charge_id,
        payment_intents.status as payment_status,
        charges.status as charge_status,
        payment_intents.currency,
        payment_intents.amount_cents,
        payment_intents.amount_received_cents,
        coalesce(charges.amount_refunded_cents, 0) as amount_refunded_cents,
        coalesce(charges.amount_captured_cents, payment_intents.amount_received_cents, 0)
            - coalesce(charges.amount_refunded_cents, 0) as net_revenue_cents,
        charges.is_paid,
        charges.is_refunded,
        charges.is_disputed,
        payment_intents.product_family,
        payment_intents.scenario,
        payment_intents.seed_batch_id,
        payment_intents.stripe_created_at,
        payment_intents.extracted_at as last_extracted_at
    from payment_intents
    left join charges
        on payment_intents.latest_charge_id = charges.charge_id
)

select *
from joined

