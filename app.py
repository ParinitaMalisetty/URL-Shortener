from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_id = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_id(num_chars=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choices(characters, k=num_chars))
        if not URLMap.query.filter_by(short_id=short_id).first():
            return short_id

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        custom_short = request.form.get('custom_short')

        if custom_short:
            if URLMap.query.filter_by(short_id=custom_short).first():
                flash('Custom short URL already taken!', 'error')
                return redirect(url_for('home'))
            short_id = custom_short
        else:
            short_id = generate_short_id()

        new_link = URLMap(original_url=original_url, short_id=short_id)
        db.session.add(new_link)
        db.session.commit()
        return render_template('index.html', short_url=request.host_url + short_id)

    return render_template('index.html')

@app.route('/<short_id>')
def redirect_short_url(short_id):
    link = URLMap.query.filter_by(short_id=short_id).first()
    if link:
        return redirect(link.original_url)
    return 'Invalid URL!', 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
