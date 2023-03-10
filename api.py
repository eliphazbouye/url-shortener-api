from flask import Flask, redirect, jsonify, request, url_for, render_template, flash
from dotenv import load_dotenv, dotenv_values
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import string
import random

config = dotenv_values(".env")
app = Flask(__name__)
app.secret_key = config['APP_KEY']
load_dotenv()

db = SQLAlchemy()

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{config['DB_USER']}:{config['DB_PASS']}@localhost/{config['DB_NAME']}"

db.init_app(app)
db.create_all()

# MODEL
class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250), unique=True, nullable=False)
    alias = db.Column(db.String(6), unique=True)
    clicks = db.Column(db.Integer, default=int(0))

    def to_json(self):
        return {
            "id": int(self.id),
            "url": str(self.url),
            "alias": str(self.alias),
            "clicks": str(self.clicks)
        }

#ROUTES
@app.post('/api/create')
def create():

    try:
        url = request.json['url']
        KEY_LEN = 5
        def base_str():
            return (string.ascii_letters+string.digits)

        def key_gen():
            keylist = [random.choice(base_str()) for i in range(KEY_LEN)]
            return "".join(keylist)

        short = Url(url=url, alias=key_gen())
        db.session.add(short)
        db.session.commit()
        return jsonify({"status": True, "message": "URL Added"})
    except IntegrityError:
        return jsonify({"status": False, "message": "URL Not Added"})


@app.route('/api/all_short')
def all_short():
    urls = db.session.query(Url).all()
    result = [url.to_json() for url in urls]
    return jsonify(result)
    

@app.route('/<alias>')
def alias(alias):
    result_query = db.session.query(Url).filter(Url.alias == alias)
    url_infos = {}
    for url in result_query:
        url_infos["url"] = url.url
        url_infos['url_clicks'] = url.clicks
        url.clicks = int(url_infos['url_clicks']) + 1
        db.session.commit()
    
    return jsonify(url_infos)

@app.delete('/api/<int:id>/delete')
def delete(id):
    alias = db.get_or_404(Url, id)
    db.session.delete(alias)
    db.session.commit()
    return jsonify({"flash": "Alias Deleted"})
