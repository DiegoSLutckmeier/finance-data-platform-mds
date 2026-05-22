with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_balance_transactions') }}
),

typed as (
    select
        object_id as balance_transaction_id,
        json_extract_string(raw_payload, '$.source') as source_id,
        json_extract_string(raw_payload, '$.type') as transaction_type,
        json_extract_string(raw_payload, '$.reporting_category') as reporting_category,
        json_extract_string(raw_payload, '$.status') as status,
        lower(json_extract_string(raw_payload, '$.currency')) as currency,
        cast(json_extract_string(raw_payload, '$.amount') as bigint) as amount_cents,
        cast(json_extract_string(raw_payload, '$.fee') as bigint) as fee_cents,
        cast(json_extract_string(raw_payload, '$.net') as bigint) as net_cents,
        json_extract_string(raw_payload, '$.description') as description,
        to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
        to_timestamp(cast(json_extract_string(raw_payload, '$.available_on') as bigint)) as available_on,
        cast(extracted_at as timestamptz) as extracted_at,
        load_id
    from bronze
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by balance_transaction_id
            order by extracted_at desc, load_id desc
        ) as row_number_latest
    from typed
)

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
    extracted_at,
    load_id
from deduplicated
where row_number_latest = 1

