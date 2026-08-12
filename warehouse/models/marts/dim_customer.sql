select customer_key, email, country
from {{ ref('stg_customers') }}
