from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:stupidblog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '1L0v3Sc0tt'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    content = db.Column(db.String(10240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner') 

    def __init__(self, email, password):
        self.email = email
        self.password = password                 


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        flash("Please log in to access that page.", 'error')
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    
    return render_template("index.html",
        users=users)

app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if email == "" or len(email) < 3:
            flash("Please enter a valid email.", 'error')
            return render_template('signup.html')

        if password == "" or len(password) < 3:
            flash("Please enter a valid password.", 'error')
            return render_template('signup.html',
                email=email)

        if password != verify:
            flash("The passwords do not match.", 'error')
            return render_template('signup.html',
                email=email)

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            flash("You have successfully signed up for a blog!", 'success')
            return redirect('/newpost')
        else:
            flash("{0} is already registered.".format(email), 'error')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            session['email'] = email
            flash("You have successfully logged in", 'success')
            return redirect('/newpost')
        
        elif email == "":
            flash("Please enter a valid email", 'error')

        elif password == "":
            flash("Please enter a password", 'error')

        elif user == None:
            flash("That user ID doesn't exist, please register or try again.", 'error')

        elif user.password != password:
            flash("Your password is incorrect.", 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    if 'email' not in session:
        return redirect('/')
    else:
        del session['email']
        flash("You have successfully signed out of your account.", 'success')
        return redirect('/')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['post_title']
        post_content = request.form['post_content']
        owner = User.query.filter_by(email=session['email']).first()
        title_error = ""
        content_error = ""
        errorcount = 0

        if post_title == "":
            errorcount += 1
            flash("You must have a title for your post.", 'error')

        if post_content == "":
            errorcount += 1
            flash("You must have content for your post.", 'error')  
    
        if errorcount > 0:
            return render_template('newpost.html',
                post_content=post_content,
                post_title=post_title,
                )
        else:
            new_entry = Blog(post_title, post_content, owner)
            db.session.add(new_entry)
            db.session.commit()
            new_id = str(new_entry.id)

            return redirect('/blog?id='+ new_id)

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()
