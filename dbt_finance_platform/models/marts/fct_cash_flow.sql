select
    balance_transaction_id,
    source_id,
    transaction_type,
    reporting_category,
    status,
    currency,
    amount_cents,
    fee_cents,
    net_cents,
    description,
    stripe_created_at,
    available_on,
    extracted_at as last_extracted_at
from {{ ref('stg_stripe_balance_transactions') }}

