with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_charges') }}
),

typed as (
    select
        object_id as charge_id,
        json_extract_string(raw_payload, '$.payment_intent') as payment_intent_id,
        json_extract_string(raw_payload, '$.customer') as customer_id,
        json_extract_string(raw_payload, '$.balance_transaction') as balance_transaction_id,
        json_extract_string(raw_payload, '$.status') as status,
        lower(json_extract_string(raw_payload, '$.currency')) as currency,
        cast(json_extract_string(raw_payload, '$.amount') as bigint) as amount_cents,
        cast(json_extract_string(raw_payload, '$.amount_captured') as bigint) as amount_captured_cents,
        cast(json_extract_string(raw_payload, '$.amount_refunded') as bigint) as amount_refunded_cents,
        cast(json_extract_string(raw_payload, '$.paid') as boolean) as is_paid,
        cast(json_extract_string(raw_payload, '$.captured') as boolean) as is_captured,
        cast(json_extract_string(raw_payload, '$.refunded') as boolean) as is_refunded,
        cast(json_extract_string(raw_payload, '$.disputed') as boolean) as is_disputed,
        json_extract_string(raw_payload, '$.failure_code') as failure_code,
        json_extract_string(raw_payload, '$.failure_message') as failure_message,
        json_extract_string(raw_payload, '$.metadata.product_family') as product_family,
        json_extract_string(raw_payload, '$.metadata.scenario') as scenario,
        json_extract_string(raw_payload, '$.metadata.seed_batch_id') as seed_batch_id,
        to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
        cast(extracted_at as timestamptz) as extracted_at,
        load_id
    from bronze
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by charge_id
            order by extracted_at desc, load_id desc
        ) as row_number_latest
    from typed
)

select
    charge_id,
    payment_intent_id,
    customer_id,
    balance_transaction_id,
    status,
    currency,
    amount_cents,
    amount_captured_cents,
    amount_refunded_cents,
    is_paid,
    is_captured,
    is_refunded,
    is_disputed,
    failure_code,
    failure_message,
    product_family,
    scenario,
    seed_batch_id,
    stripe_created_at,
    extracted_at,
    load_id
from deduplicated
where row_number_latest = 1

