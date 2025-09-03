from src.sql import SqlTemplate

# Import all SQL templates for news module
list_news = SqlTemplate("src/sql/news/list_news.sql")
get_single_news = SqlTemplate("src/sql/news/get_single_news.sql") 
insert_news = SqlTemplate("src/sql/news/insert_news.sql")
update_news = SqlTemplate("src/sql/news/update_news.sql")
delete_news = SqlTemplate("src/sql/news/delete_news.sql")
get_news_author = SqlTemplate("src/sql/news/get_news_author.sql")
