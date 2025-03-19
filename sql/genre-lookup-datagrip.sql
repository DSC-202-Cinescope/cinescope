-- Determine the average of all vote scores for the movies
WITH avg_vote AS (
    SELECT AVG(m.vote_average) AS avg_vote
    FROM movies AS m
),
-- Determine the average amount of votes that were cast for the movies. Also find the Max value.
    avg_votes_cast AS (
    SELECT
        AVG(m.vote_count) AS avg_count,
        MAX(m.vote_count) AS max_count
    FROM movies AS m
),
-- Build a classification scheme for the vote score and vote counts
    avg_vote_score AS (
    SELECT
        m.id,
        avc.max_count,
        avc.avg_count,
        -- Conditional to determine if a vote is considered a high, medium, or low vote score.
        -- Checks the average score of a single movie and compares it to the average score of all movies
        CASE
            WHEN m.vote_average >= (av.avg_vote * 1.5) THEN 'High'
            WHEN m.vote_average >= (av.avg_vote * 0.5) THEN 'Medium'
            ELSE 'Low'
        END AS score,
        -- Conditional to determine if a count is considered high, medium, or low
        -- Check if the log of the vote_count is greater than or equal to the log (base 10 or 2), of the average count.
        -- Use nullif to avoid taking the log of 0 since an error will be raised.
        CASE
            WHEN LN(NULLIF(m.vote_count, 0)) >= LN(NULLIF(avc.avg_count, 0) * 10) THEN 'High'
            WHEN LN(NULLIF(m.vote_count, 0)) >= LN(NULLIF(avc.avg_count, 0) * 2) THEN 'Medium'
            ELSE 'Low'
        END AS vote_count
    FROM movies AS m
    -- Cross Join avg_vote and avg_votes_cast CTE tables
    CROSS JOIN avg_vote AS av
    CROSS JOIN avg_votes_cast AS avc
),
-- Determine rank of a cast or crew member based on popularity
    cast_ranking AS (
        SELECT
            am.movie_id,
            a.name,
            a.popularity,
            -- Row number over to apply a sequence for our ranking
            -- Partition by the movie id then for each movie id order based of actor popularity
            ROW_NUMBER() OVER (PARTITION BY am.movie_id ORDER BY a.popularity DESC) AS ranking
        FROM actor_movies AS am
        JOIN actors a ON am.actor_id = a.id
),
-- Cast List will output an array of the top 5 most popular members of the case
    cast_list AS (
        SELECT
            cr.movie_id,
            -- output an array where we order by the ranking popularity
            -- Filter the results where the ranking is the top 5 cast members
            ARRAY_AGG(cr.name ORDER BY cr.popularity DESC) FILTER ( WHERE ranking <= 5 ) AS movie_cast
        FROM cast_ranking AS cr
        GROUP BY cr.movie_id
)
-- Structure the main query
SELECT
    m.title AS Movie,
    avs.score AS viewer_score_classification,
    m.vote_average,
    avs.vote_count AS vote_classification,
    ln(NULLIF(m.vote_count, 0)) AS vote_count,
    cl.movie_cast
FROM movies as m
-- Join our tables on our id's
-- JOIN movie_ids mi ON m.id = mi.id
JOIN avg_vote_score avs ON m.id = avs.id
JOIN cast_list cl ON m.id = cl.movie_id
-- Where exists will be select our genre from the genre json array
-- The subquery allows the user to select the genre based on genre id
WHERE EXISTS (
    SELECT 1
    FROM JSONB_ARRAY_ELEMENTS(m.genres) AS genre
    WHERE (genre ->> 'id')::INTEGER = 28 -- 28 is the 'Action' genre, 16 is 'Animation'
)
AND m.original_language = 'en'
-- Group by clause
GROUP BY cl.movie_cast, m.id, avs.score, m.vote_average, avs.vote_count, m.vote_count, m.title
-- Order first by our vote_counts that are high. Then enter a conditional to to use high vote counts to
-- organize by vote average. When there is a tie in the vote average we then refer back to the vote count
-- and sub-order by vote count. I.E Find movies with High vote counts, order by vote average, when a tie in the average
-- order then by vote count.
ORDER BY
    (avs.vote_count = 'High') DESC,
    CASE
        WHEN avs.vote_count = 'High' THEN m.vote_average
        ELSE m.vote_count
    END DESC,
    m.vote_count DESC
-- Limit to the top 5 results
LIMIT 5;
