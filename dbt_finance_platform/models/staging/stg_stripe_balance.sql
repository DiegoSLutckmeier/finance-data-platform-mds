with bronze as (
    select *
    from {{ source('stripe_bronze', 'stripe_balance') }}
)

select
    object_id as balance_snapshot_id,
    json_extract(raw_payload, '$.available') as available_balances,
    json_extract(raw_payload, '$.pending') as pending_balances,
    cast(json_extract_string(raw_payload, '$.livemode') as boolean) as is_livemode,
    to_timestamp(cast(json_extract_string(raw_payload, '$.created') as bigint)) as stripe_created_at,
    cast(extracted_at as timestamptz) as extracted_at,
    load_id
from bronze

