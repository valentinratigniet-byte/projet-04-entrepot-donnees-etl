select
    id       as customer_key,
    email,
    country
from {{ source('raw', 'customer') }}
