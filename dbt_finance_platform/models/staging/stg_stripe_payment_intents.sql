with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_payment_intents') }}
),

typed as (
    select
        object_id as payment_intent_id,
        json_extract_string(raw_payload, '$.customer') as customer_id,
        json_extract_string(raw_payload, '$.latest_charge') as latest_charge_id,
        json_extract_string(raw_payload, '$.status') as status,
        lower(json_extract_string(raw_payload, '$.currency')) as currency,
        cast(json_extract_string(raw_payload, '$.amount') as bigint) as amount_cents,
        cast(json_extract_string(raw_payload, '$.amount_received') as bigint) as amount_received_cents,
        json_extract_string(raw_payload, '$.metadata.product_family') as product_family,
        json_extract_string(raw_payload, '$.metadata.scenario') as scenario,
        json_extract_string(raw_payload, '$.metadata.seed_batch_id') as seed_batch_id,
        to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
        cast(extracted_at as timestamptz) as extracted_at,
        load_id,
        raw_payload
    from bronze
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by payment_intent_id
            order by extracted_at desc, load_id desc
        ) as row_number_latest
    from typed
)

select
    payment_intent_id,
    customer_id,
    latest_charge_id,
    status,
    currency,
    amount_cents,
    amount_received_cents,
    product_family,
    scenario,
    seed_batch_id,
    stripe_created_at,
    extracted_at,
    load_id
from deduplicated
where row_number_latest = 1
