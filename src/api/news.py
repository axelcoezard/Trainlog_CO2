import logging
from datetime import datetime

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from src.pg import pg_session
from src.sql import news as news_sql
from src.utils import getUser, isCurrentTrip, lang, owner_required, owner

logger = logging.getLogger(__name__)

news_blueprint = Blueprint("news", __name__)


@news_blueprint.route("/news")
def news(username=None):
    """Display news page"""
    userinfo = session.get("userinfo", {})
    current_user = userinfo.get("logged_in_user")
    
    with pg_session() as pg:
        result = pg.execute(news_sql.list_news()).fetchall()
        
        # Convert to list of dictionaries
        news_list = []
        for item in result:
            author_display = 'admin' if item[3] == owner else item[3]
            news_dict = {
                'id': item[0],
                'title': item[1],
                'content': item[2],
                'author_display': author_display,
                'created': item[4],
                'last_modified': item[5]
            }
            news_list.append(news_dict)

    return render_template(
        'news.html',
        username=current_user,
        news_list=news_list,
        **lang.get(userinfo.get("lang", "en"), {}),
        **userinfo,
        nav="bootstrap/navigation.html" if current_user != "public" else "bootstrap/no_user_nav.html",
        isCurrent=isCurrentTrip(getUser()) if current_user != "public" else False
    )


@news_blueprint.route("/<username>/news/submit", methods=["POST"])
@owner_required
def submit_news(username):
    """Submit a new news item (owner only)"""
    title = request.form["title"]
    content = request.form["content"]
    current_user = session["userinfo"]["logged_in_user"]
    
    with pg_session() as pg:
        result = pg.execute(
            news_sql.insert_news(),
            {
                "title": title,
                "content": content,
                "username": current_user
            }
        ).fetchone()
    
    return redirect(url_for("news.news"))


@news_blueprint.route("/<username>/news/edit", methods=["POST"])
@owner_required
def edit_news(username):
    """Edit a news item (owner only)"""
    news_id = request.form["news_id"]
    title = request.form["title"]
    content = request.form["content"]
    
    with pg_session() as pg:
        pg.execute(
            news_sql.update_news(),
            {
                "news_id": news_id,
                "title": title,
                "content": content
            }
        )
    
    return redirect(url_for("news.news"))


@news_blueprint.route("/<username>/news/delete", methods=["POST"])
@owner_required
def delete_news(username):
    """Delete a news item (owner only)"""
    news_id = request.form["news_id"]
    
    with pg_session() as pg:
        pg.execute(
            news_sql.delete_news(),
            {"news_id": news_id}
        )
    
    return redirect(url_for("news.news"))


@news_blueprint.route("/news/<int:news_id>/details")
def get_news_details(news_id):
    """Get news details for editing"""
    with pg_session() as pg:
        result = pg.execute(
            news_sql.get_single_news(),
            {"news_id": news_id}
        ).fetchone()
        
        if result:
            return jsonify({
                'id': result[0],
                'title': result[1],
                'content': result[2],
                'author': result[3]
            })
        else:
            return jsonify({'error': 'News item not found'}), 404