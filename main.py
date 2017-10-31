from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

#DRY helper functions
def is_blank(field):
    if field == '':
        return True
    else:
        return False
def len_test(field, min, max):
    if len(field) < min or len(field) > max:
        return True
    else:
        return False

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_un = db.Column(db.String(120), db.ForeignKey('user.username'))

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
        
"""@app.context_processor
def userhomepage():
    return dict(session=session['username'])      """

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
        if not user:
            flash('User with this Username does not exist', 'error')
        elif user and user.password != password:
            flash('Password for this Username is incorrect', 'error')
            return render_template('login.html', username=username, navclasslogin='active')
        else:
            session['username'] = username
            flash("Logged in", "info")
            return redirect('/newpost')   

    return render_template('login.html', navclasslogin='active')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if is_blank(username):
            flash('Username Field is Blank', 'error')
            return render_template('signup.html', password=password, verify=verify)
        if is_blank(password):
            flash('Password Field is Blank', 'error')
            return render_template('signup.html', username=username, verify=verify)  
        if is_blank(verify):
            flash('Verify Password Field is Blank', 'error')
            return render_template('signup.html', username=username, password=password)   
        if password != verify:
            flash("Verify Password does't match Password" , 'error')
            return render_template('signup.html', username=username)
        if len_test(username, 3, 20):
            flash('Username must be 3 - 20 characters in length', 'error')
            return render_template('signup.html', password=password, verify=verify)
        if len_test(password, 3, 20):
            flash('Password must be 3 - 20 characters in length', 'error')
            return render_template('signup.html', username=username)
        if existing_user:
            flash('Duplicate user', 'error')
            return render_template('signup.html', password=password, verify=verify)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('Successfully Logged Out', 'green')
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title='Users', users=users, home='active')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if blog_title == '':
            flash('Blog Title cannot be empty', 'error')
            return render_template('newpost.html',navclassnewpost='active', body=blog_body )
        elif blog_body == '':
            flash('Blog Body cannot be empty', 'error')
            return render_template('newpost.html',navclassnewpost='active', titlec=blog_title)
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.get(new_blog.id)
            return render_template('indblog.html',blog=blog)
            
               
    
    return render_template('newpost.html',title="New Blog Post",navclassnewpost='active')

@app.route('/blog', methods=['POST', 'GET'])
def display_blogs():
    if request.method == 'GET':
        blog_id = request.args.get('id')
        user_id = request.args.get('user')
        if blog_id == None and user_id == None:
            blogs = Blog.query.all()
            return  render_template('listings.html',title="All Blog Posts", 
            blogs=blogs,navclassmainblog='active')
        elif user_id == None:
            blog = Blog.query.get(blog_id)
            return render_template('indblog.html',title='', blog=blog)
        else:
            owner = User.query.filter_by(username=user_id).first()
            blogs = Blog.query.filter_by(owner=owner).all()
            return render_template('userpage.html', title="", blogs=blogs, user=owner, navclassmainmyposts='active')
"""
    elif request.method == 'POST':
        zxzxzx x zczxZxXXZ = username
        blogs = Blog.query.filter_by(owner=session['username']).all()
        return render_template('userpage.html', title="Yoour Blogs", blogs=blogs, user=owner, navclassmainmyposts='active')
        """
            
            
if __name__ == '__main__':
    app.run()