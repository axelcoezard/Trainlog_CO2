INSERT INTO news (title, content, username)
VALUES (:title, :content, :username)
RETURNING id