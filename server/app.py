#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
from flask_migrate import Migrate

from models import db, Article

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'  # Secret key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Route to clear the session (reset page views)
@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data'}, 200

# Route to return all articles
@app.route('/articles')
def index_articles():
    articles = [article.to_dict() for article in Article.query.all()]
    return make_response(jsonify(articles), 200)

# Route to return a single article and track page views
@app.route('/articles/<int:id>')
def show_article(id):
    # Initialize page_views if not set
    session['page_views'] = session.get('page_views') or 0
    session['page_views'] += 1

    # Look up the article
    article = Article.query.filter(Article.id == id).first()
    if not article:
        return {'error': 'Article not found'}, 404

    # Allow viewing only if user has viewed 3 or fewer articles
    if session['page_views'] <= 3:
        return article.to_dict(), 200

    # Return paywall message after 3 views
    return {'message': 'Maximum pageview limit reached'}, 401

if __name__ == '__main__':
    app.run(port=5555)
