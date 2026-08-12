select
    order_id,
    product_id                as product_key,
    quantity,
    unit_price,
    quantity * unit_price      as line_amount
from {{ source('raw', 'order_item') }}
