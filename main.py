from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bab@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if blog_title == '' or blog_body == '':
            errormsg='Blog Title and Blog Body must not be empty'
            return render_template('newpost.html',title="Error",errormsg=errormsg,navclassnewpost='active')
        else:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.get(new_blog.id)
            return render_template('indblog.html',title='blog', blog=blog)
            
               
    
    return render_template('newpost.html',title="New Blog",navclassnewpost='active')

@app.route('/blog', methods=['POST', 'GET'])
def display_blogs():
    if request.method == 'GET':
        blog_id = request.args.get('id')
        if blog_id == None:
            blogs = Blog.query.all()
            return  render_template('listings.html',title="Build A Blog", 
            blogs=blogs,navclassmainblog='active')
        else:
            blog = Blog.query.get(blog_id)
            return render_template('indblog.html',title='blog', blog=blog)
    
if __name__ == '__main__':
    app.run()