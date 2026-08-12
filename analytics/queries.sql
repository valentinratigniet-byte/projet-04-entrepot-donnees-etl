-- =====================================================================
-- Requêtes analytiques de validation (entrepôt DuckDB).
-- Montrent que le schéma en étoile est interrogeable et que les 3 sources
-- se croisent (ventes × météo × temps).
-- Exécuter : duckdb warehouse/warehouse.duckdb < analytics/queries.sql
-- =====================================================================

-- Q1 — CA mensuel (fait × dimension date)
SELECT d.annee_mois, count(DISTINCT f.order_id) AS commandes,
       round(sum(f.line_amount), 0) AS ca
FROM marts.fct_sales f
JOIN marts.dim_date d ON d.date_key = f.date_key
GROUP BY 1 ORDER BY 1;

-- Q2 — Ventes selon la météo (croisement multi-sources : ventes × API météo)
SELECT d.est_pluvieux,
       count(DISTINCT f.order_id) AS commandes,
       round(sum(f.line_amount), 0) AS ca
FROM marts.fct_sales f
JOIN marts.dim_date d ON d.date_key = f.date_key
WHERE d.temp_mean IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- Q3 — Ventes par tranche de température
SELECT d.temp_bucket,
       count(DISTINCT f.order_id) AS commandes,
       round(sum(f.line_amount), 0) AS ca
FROM marts.fct_sales f
JOIN marts.dim_date d ON d.date_key = f.date_key
WHERE d.temp_bucket IS NOT NULL
GROUP BY 1 ORDER BY 3 DESC;

-- Q4 — Top catégories (fait × dimension produit)
SELECT p.category, round(sum(f.line_amount), 0) AS ca
FROM marts.fct_sales f
JOIN marts.dim_product p ON p.product_key = f.product_key
GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
