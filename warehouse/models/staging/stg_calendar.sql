select date from {{ source('raw', 'calendar') }}
