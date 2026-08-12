select
    date,
    temp_mean,
    precip
from {{ source('raw', 'weather') }}
