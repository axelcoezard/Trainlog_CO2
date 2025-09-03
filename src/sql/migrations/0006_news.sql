-- News table
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    username TEXT NOT NULL,
    created TIMESTAMP DEFAULT now(),
    last_modified TIMESTAMP DEFAULT now()
);