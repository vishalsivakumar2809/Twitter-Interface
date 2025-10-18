SELECT * from follows
where flwer = 6;

SELECT * from tweets 
where writer = 293;

SELECT * from retweets
where usr = 293;

WITH combined AS (
    SELECT 
        tweets.tid AS tweet_id,
        tweets.writer AS writer,
        tweets.tdate AS date,
        'tweet' AS type
    FROM 
        tweets
    JOIN 
        follows ON tweets.writer = follows.flwee
    WHERE 
        follows.flwer = 6
    UNION ALL
    SELECT 
        retweets.tid AS tweet_id,
        retweets.usr AS writer,
        retweets.rdate AS date,
        'retweet' AS type
    FROM 
        retweets
    JOIN 
        follows ON retweets.usr = follows.flwee
    WHERE 
        follows.flwer = 6
),
max_dates AS (
    SELECT 
        tweet_id, 
        writer, 
        MAX(date) AS max_date
    FROM 
        combined
    GROUP BY 
        tweet_id, writer
)
SELECT 
    DISTINCT
    c.tweet_id, 
    c.writer, 
    c.date,
    c.type
FROM 
    combined c
JOIN 
    max_dates m ON c.tweet_id = m.tweet_id AND c.writer = m.writer AND c.date = m.max_date
ORDER BY 
    date DESC;
