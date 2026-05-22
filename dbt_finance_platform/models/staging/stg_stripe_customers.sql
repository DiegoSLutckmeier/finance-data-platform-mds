with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_customers') }}
),

typed as (
    select
        object_id as customer_id,
        json_extract_string(raw_payload, '$.email') as email,
        json_extract_string(raw_payload, '$.name') as customer_name,
        json_extract_string(raw_payload, '$.metadata.country') as country,
        json_extract_string(raw_payload, '$.metadata.segment') as customer_segment,
        json_extract_string(raw_payload, '$.metadata.seed_batch_id') as seed_batch_id,
        cast(json_extract_string(raw_payload, '$.balance') as bigint) as balance_cents,
        cast(json_extract_string(raw_payload, '$.delinquent') as boolean) as is_delinquent,
        to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
        cast(extracted_at as timestamptz) as extracted_at,
        load_id
    from bronze
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by customer_id
            order by extracted_at desc, load_id desc
        ) as row_number_latest
    from typed
)

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
    extracted_at,
    load_id
from deduplicated
where row_number_latest = 1
