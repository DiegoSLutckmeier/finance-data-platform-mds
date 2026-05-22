with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_payouts') }}
),

typed as (
    select
        object_id as payout_id,
        json_extract_string(raw_payload, '$.balance_transaction') as balance_transaction_id,
        json_extract_string(raw_payload, '$.status') as status,
        lower(json_extract_string(raw_payload, '$.currency')) as currency,
        cast(json_extract_string(raw_payload, '$.amount') as bigint) as amount_cents,
        json_extract_string(raw_payload, '$.arrival_date') as arrival_date_raw,
        json_extract_string(raw_payload, '$.description') as description,
        json_extract_string(raw_payload, '$.method') as payout_method,
        json_extract_string(raw_payload, '$.type') as payout_type,
        to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
        cast(extracted_at as timestamptz) as extracted_at,
        load_id
    from bronze
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by payout_id
            order by extracted_at desc, load_id desc
        ) as row_number_latest
    from typed
)

select
    payout_id,
    balance_transaction_id,
    status,
    currency,
    amount_cents,
    arrival_date_raw,
    description,
    payout_method,
    payout_type,
    stripe_created_at,
    extracted_at,
    load_id
from deduplicated
where row_number_latest = 1

