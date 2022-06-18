from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class URLs(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(3))
    
    def __init__(self, long, short):
        self.long = long
        self.short = short

## INitialize DB
@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase ## Get's all possible letters
    while True:
        random_letters = random.choices(letters, k=3) ## 'k' param gives the amount of letters we we'll use.
        random_letters = ''.join(random_letters)
        shortened_url = URLs.query.filter_by(short=random_letters).first()
        if not shortened_url:
            return random_letters

## MAIN ROUTE
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        url_received = request.form['url-link']
        url_exists = URLs.query.filter_by(long=url_received).first()
        if url_exists:
            return redirect(url_for('display_new_url', url=url_exists.short))
        else:
            shortened_url = shorten_url()
            new_url = URLs(url_received, shortened_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for('display_new_url', url=shortened_url))
    else:
        return render_template('home.html')

@app.route('/new_url/<url>')
def display_new_url(url):
    return render_template('shortened_url.html', short_url_display=url)

@app.route('/<shortened_url>')
def redirect_user(shortened_url):
    og_url = URLs.query.filter_by(short=shortened_url).first()
    if og_url:
        return redirect(og_url.long)
    else:
        return f'<h1>URL Does Not Exist.</h1>'

if __name__ == '__main__':
    app.run(debug=True)