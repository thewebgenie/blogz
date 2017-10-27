from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'display_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in", "success")
            return redirect('/')
        else:
            # TODO - explain why login failed
            flash('User password incorrect, or user does not exist', 'error')
            

    return render_template('login.html', navclasslogin='active')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title="Yoour Blogs", users=users,home='active')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if blog_title == '' or blog_body == '':
            errormsg='Blog Title and Blog Body must not be empty'
            return render_template('newpost.html',title="Error",errormsg=errormsg,navclassnewpost='active')
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.get(new_blog.id)
            return render_template('indblog.html',title='blog', blog=blog)
            
               
    
    return render_template('newpost.html',title="New Blog",navclassnewpost='active')

@app.route('/blog', methods=['POST', 'GET'])
def display_blogs():
    if request.method == 'GET':
        blog_id = request.args.get('id')
        user_id = request.args.get('user')
        if blog_id == None and user_id == None:
            blogs = Blog.query.all()
            return  render_template('listings.html',title="Build A Blog", 
            blogs=blogs,navclassmainblog='active')
        elif user_id == None:
            blog = Blog.query.get(blog_id)
            return render_template('indblog.html',title='blog', blog=blog)
        else:
            owner = User.query.filter_by(username=session['username']).first()
            blogs = Blog.query.filter_by(owner=owner).all()
            return render_template('userpage.html', title="Yoour Blogs", blogs=blogs, user=owner, navclassmainmyposts='active')
    
if __name__ == '__main__':
    app.run()