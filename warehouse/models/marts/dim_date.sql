-- Dimension date = calendrier généré ENRICHI par la météo (API).
-- C'est ici que 2 des 3 sources se rejoignent dans l'étoile.
with cal as (select date from {{ ref('stg_calendar') }}),
     w   as (select date, temp_mean, precip from {{ ref('stg_weather') }})
select
    cast(strftime(cal.date, '%Y%m%d') as integer) as date_key,
    cal.date,
    extract(year    from cal.date)                as annee,
    extract(quarter from cal.date)                as trimestre,
    extract(month   from cal.date)                as mois,
    strftime(cal.date, '%Y-%m')                   as annee_mois,
    (dayofweek(cal.date) in (0, 6))               as est_weekend,
    w.temp_mean,
    w.precip,
    (w.precip > 1.0)                              as est_pluvieux,
    case
        when w.temp_mean is null then null
        when w.temp_mean < 5  then 'Froid'
        when w.temp_mean < 18 then 'Doux'
        else 'Chaud'
    end                                           as temp_bucket
from cal
left join w on w.date = cal.date
