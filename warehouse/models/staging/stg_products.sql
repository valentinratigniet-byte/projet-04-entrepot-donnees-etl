select
    p.id     as product_key,
    p.sku,
    p.name   as product_name,
    c.name   as category,
    p.price
from {{ source('raw', 'product') }} p
join {{ source('raw', 'category') }} c on c.id = p.category_id
