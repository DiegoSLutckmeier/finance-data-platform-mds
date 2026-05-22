select
    customer_id,
    email,
    customer_name,
    country,
    customer_segment,
    seed_batch_id,
    balance_cents,
    is_delinquent,
    stripe_created_at,
    extracted_at as last_extracted_at
from {{ ref('stg_stripe_customers') }}

