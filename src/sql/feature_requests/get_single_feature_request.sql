SELECT 
    id,
    title,
    description,
    username,
    status,
    created,
    upvotes,
    downvotes,
    score
FROM feature_requests
WHERE id = :request_id