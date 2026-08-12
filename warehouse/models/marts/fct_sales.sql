-- Table de faits (grain : une ligne de commande), reliée aux 3 dimensions.
select
    oi.order_id,
    o.customer_key,
    oi.product_key,
    cast(strftime(o.order_date, '%Y%m%d') as integer) as date_key,
    o.status,
    oi.quantity,
    oi.unit_price,
    oi.line_amount
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o on o.order_id = oi.order_id
