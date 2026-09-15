SELECT COUNT(*) AS number_of_cities
FROM cities;

--------------------------------------------------------------

SELECT
    MAX(temperature_2m_max) AS maximum_temperature
FROM weather_forecasts;

----------------------------------------------------------------

SELECT
    MAX(precipitation_sum) AS maximum_precipitation
FROM weather_forecasts;

----------------------------------------------------------------

SELECT
    MAX(weather_risk_score) AS maximum_risk_score
FROM weather_risks;

----------------------------------------------------------------

SELECT
    c.name AS city,
    MAX(wf.temperature_2m_max) AS max_temperature
FROM weather_forecasts wf
JOIN cities c ON c.id = wf.city_id
GROUP BY c.name
ORDER BY max_temperature DESC;

--------------------------------------------------------------


SELECT
    c.name AS city,
    MAX(wf.temperature_2m_max) AS max_temperature
FROM weather_forecasts wf
JOIN cities c ON c.id = wf.city_id
GROUP BY c.name
ORDER BY max_temperature DESC;

-------------------------------------------------------------------

SELECT
    c.name AS city,
    MAX(wf.precipitation_sum) AS max_precipitation
FROM weather_forecasts wf
JOIN cities c ON c.id = wf.city_id
GROUP BY c.name
ORDER BY max_precipitation DESC;

--------------------------------------------------------------------

SELECT
    c.name AS city,
    ROUND(AVG(wr.weather_risk_score), 2) AS average_risk
FROM weather_risks wr
JOIN cities c ON c.id = wr.city_id
GROUP BY c.name
ORDER BY average_risk DESC;

---------------------------------------------------------------------

SELECT
    c.name AS city,
    wr.date,
    wr.weather_risk_score,
    wr.weather_risk_category,
    wr.delivery_impact
FROM weather_risks wr
JOIN cities c ON c.id = wr.city_id
ORDER BY wr.weather_risk_score DESC
LIMIT 20;

----------------------------------------------------------------------

SELECT
    c.name AS city,
    wr.date,
    wr.weather_risk_score,
    wr.weather_risk_category,
    wr.delivery_impact
FROM weather_risks wr
JOIN cities c ON c.id = wr.city_id
WHERE wr.weather_risk_score = (
    SELECT MAX(wr2.weather_risk_score)
    FROM weather_risks wr2
    WHERE wr2.city_id = wr.city_id
)
ORDER BY wr.weather_risk_score DESC;

---------------------------------------------------------------------

SELECT COUNT(*) AS number_of_cities
FROM cities;

---------------------------------------------------------------------

SELECT
    MAX(temperature_2m_max) AS maximum_temperature
FROM weather_forecasts;

---------------------------------------------------------------------

SELECT
    weather_risk_category,
    COUNT(*) AS number_of_forecasts
FROM weather_risks
GROUP BY weather_risk_category
ORDER BY number_of_forecasts DESC;

---------------------------------------------------------------------

SELECT
    c.name AS city,
    COUNT(*) AS weekend_disruptions
FROM weather_risks wr
JOIN cities c ON c.id = wr.city_id
WHERE wr.is_weekend = TRUE
  AND wr.delivery_impact <> 'Low Impact'
GROUP BY c.name
ORDER BY weekend_disruptions DESC;

----------------------------------------------------------------------

SELECT
    CASE
        WHEN is_weekend = TRUE THEN 'Weekend'
        ELSE 'Weekday'
    END AS period,
    COUNT(*) AS affected_forecasts
FROM weather_risks
WHERE delivery_impact <> 'Low Impact'
GROUP BY is_weekend
ORDER BY affected_forecasts DESC;

---------------------------------------------------------------------

SELECT
    c.name AS city,
    ROUND(AVG(wr.weather_risk_score), 2) AS average_weekday_risk
FROM weather_risks wr
JOIN cities c ON c.id = wr.city_id
WHERE wr.is_weekend = FALSE
GROUP BY c.name
ORDER BY average_weekday_risk DESC;

----------------------------------------------------------------------

SELECT
    delivery_impact,
    COUNT(*) AS number_of_periods
FROM weather_risks
GROUP BY delivery_impact
ORDER BY number_of_periods DESC;