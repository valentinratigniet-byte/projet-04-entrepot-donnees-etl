select product_key, sku, product_name, category, price
from {{ ref('stg_products') }}
