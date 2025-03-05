WITH avg_vote AS (
    SELECT AVG(m.vote_average) AS avg_vote -- 2.144 is the average
    FROM movies AS m
),
    avg_votes_cast AS (
    SELECT AVG(m.vote_count) AS avg_count
    FROM movies AS m
),
    avg_vote_score AS (
    SELECT
        m.id,
        CASE
            WHEN m.vote_average >= (av.avg_vote * 1.5) THEN 'High'
            WHEN m.vote_average >= (av.avg_vote * 0.5) THEN 'Medium'
            ELSE 'Low'
        END AS score,
        CASE
            WHEN m.vote_count >= (avc.avg_count * 750) THEN 'High'
            WHEN m.vote_count >= (avc.avg_count * 375) THEN 'Medium'
            ELSE 'Low'
        END AS vote_count
    FROM movies AS m
    CROSS JOIN avg_vote AS av
    CROSS JOIN avg_votes_cast AS avc
),
    cast_list AS (
        SELECT
            am.movie_id,
            ARRAY_AGG(a.name ORDER BY a.popularity DESC) AS movie_cast
        FROM actor_movies AS am
        JOIN actors a ON am.actor_id = a.id
        GROUP BY am.movie_id
    )
SELECT
    m.title AS Movie,
    avs.score AS viewer_score_classification,
    m.vote_average,
    avs.vote_count AS vote_classification,
    m.vote_count,
    cl.movie_cast
FROM movies as m
JOIN movie_ids mi ON m.id = mi.id
JOIN avg_vote_score avs ON m.id = avs.id
JOIN cast_list cl ON m.id = cl.movie_id
WHERE EXISTS (SELECT 1
              FROM JSONB_ARRAY_ELEMENTS(m.genres) AS genre
              WHERE (genre ->> 'id')::INTEGER = 28) -- 28 is the 'Action' genre, 16 is 'Animation
GROUP BY cl.movie_cast, m.id, avs.score, m.vote_average, avs.vote_count, m.vote_count, m.title
ORDER BY
    (avs.vote_count = 'High') DESC,
    CASE
        WHEN avs.vote_count = 'High' THEN m.vote_average
        ELSE m.vote_count
    END DESC,
    m.vote_count DESC

LIMIT 5
;