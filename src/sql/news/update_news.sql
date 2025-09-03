UPDATE news 
SET title = :title, 
    content = :content,
    last_modified = now()
WHERE id = :news_id