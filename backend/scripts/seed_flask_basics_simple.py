#!/usr/bin/env python3
"""
Simplified seed script for Flask Basics tutorial content.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import LearningModule, Lesson, Exercise, ExerciseHint
from sqlalchemy import text


def create_flask_basics_content():
    """Create Flask basics tutorial content."""
    db = SessionLocal()
    
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        print("Database connection successful")
        
        # Create Flask Basics Learning Module
        flask_module = LearningModule(
            name="Flask Basics",
            description="Learn Flask web framework fundamentals including routing, templates, forms, and database integration",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=240
        )
        db.add(flask_module)
        db.commit()
        db.refresh(flask_module)
        print(f"Created Flask Basics module: {flask_module.id}")
        
        # Lesson 1: Introduction to Flask and Basic Routing
        lesson1_content = """# Introduction to Flask and Basic Routing

## What is Flask?

Flask is a lightweight and flexible Python web framework that provides the basic tools and libraries to build web applications.

## Installing Flask

```bash
pip install Flask
```

## Your First Flask Application

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

## Understanding Routes

Routes define URL patterns and map them to Python functions using the `@app.route()` decorator.

### Basic Route Examples

```python
@app.route('/')
def home():
    return 'Home Page'

@app.route('/about')
def about():
    return 'About Page'
```

### Dynamic Routes

```python
@app.route('/user/<username>')
def user_profile(username):
    return f'Hello, {username}!'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post ID: {post_id}'
```
"""
        
        lesson1 = Lesson(
            module_id=flask_module.id,
            title="Introduction to Flask and Basic Routing",
            content=lesson1_content,
            order_index=1,
            estimated_duration=45
        )
        db.add(lesson1)
        db.commit()
        db.refresh(lesson1)
        print(f"Created Lesson 1: {lesson1.id}")
        
        # Exercise 1.1: Create Basic Flask App
        exercise1_1 = Exercise(
            lesson_id=lesson1.id,
            title="Create Your First Flask Application",
            description="Create a basic Flask application with a home route that returns 'Welcome to Flask!'",
            exercise_type="coding",
            starter_code="""# Import Flask
from flask import Flask

# Create your Flask app instance here


# Create a route for the home page ('/') that returns 'Welcome to Flask!'


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
""",
            solution_code="""from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to Flask!'

if __name__ == '__main__':
    app.run(debug=True)
""",
            points=10,
            order_index=1,
            difficulty="easy"
        )
        db.add(exercise1_1)
        db.commit()
        db.refresh(exercise1_1)
        
        # Add hints for exercise 1.1
        hint1 = ExerciseHint(
            exercise_id=exercise1_1.id,
            hint_text="Start by creating a Flask instance: app = Flask(__name__)",
            order_index=1
        )
        db.add(hint1)
        db.commit()
        
        hint2 = ExerciseHint(
            exercise_id=exercise1_1.id,
            hint_text="Use the @app.route('/') decorator to define the home route",
            order_index=2
        )
        db.add(hint2)
        db.commit()
        
        hint3 = ExerciseHint(
            exercise_id=exercise1_1.id,
            hint_text="The function should return the string 'Welcome to Flask!'",
            order_index=3
        )
        db.add(hint3)
        db.commit()
        
        # Exercise 1.2: Dynamic Routes
        exercise1_2 = Exercise(
            lesson_id=lesson1.id,
            title="Create Dynamic Routes",
            description="Create a Flask app with a dynamic route '/user/<name>' that greets the user by name",
            exercise_type="coding",
            starter_code="""from flask import Flask

app = Flask(__name__)

# Create a dynamic route '/user/<name>' that returns 'Hello, <name>!'


if __name__ == '__main__':
    app.run(debug=True)
""",
            solution_code="""from flask import Flask

app = Flask(__name__)

@app.route('/user/<name>')
def user_greeting(name):
    return f'Hello, {name}!'

if __name__ == '__main__':
    app.run(debug=True)
""",
            points=15,
            order_index=2,
            difficulty="easy"
        )
        db.add(exercise1_2)
        db.commit()
        print(f"Created 2 exercises for Lesson 1")
        
        # Lesson 2: Templates and Static Files
        lesson2_content = """# Templates and Static Files in Flask

## Introduction to Templates

Templates separate HTML from Python code using the Jinja2 templating engine.

## Basic Template Usage

### Python Code (app.py)
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='Home Page')
```

### Template File (templates/index.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>Welcome to Flask!</h1>
</body>
</html>
```

## Template Variables

Pass data from routes to templates:

```python
@app.route('/profile/<username>')
def profile(username):
    user_data = {
        'name': username,
        'email': f'{username}@example.com'
    }
    return render_template('profile.html', user=user_data)
```

## Static Files

Static files (CSS, JavaScript, images) go in the `static` folder:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```
"""
        
        lesson2 = Lesson(
            module_id=flask_module.id,
            title="Templates and Static Files",
            content=lesson2_content,
            order_index=2,
            estimated_duration=60
        )
        db.add(lesson2)
        db.commit()
        db.refresh(lesson2)
        print(f"Created Lesson 2: {lesson2.id}")
        
        # Exercise 2.1: Basic Template
        exercise2_1 = Exercise(
            lesson_id=lesson2.id,
            title="Create a Basic Template",
            description="Create a Flask app that uses a template to display a welcome message with the user's name",
            exercise_type="coding",
            starter_code="""from flask import Flask, render_template

app = Flask(__name__)

# Create a route that renders a template with a name variable
# Route should be '/welcome/<name>'
# Template should display: <h1>Welcome, {{ name }}!</h1>


if __name__ == '__main__':
    app.run(debug=True)
""",
            solution_code="""from flask import Flask, render_template

app = Flask(__name__)

@app.route('/welcome/<name>')
def welcome(name):
    return render_template('welcome.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)

# Template file: templates/welcome.html
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Welcome</title>
# </head>
# <body>
#     <h1>Welcome, {{ name }}!</h1>
# </body>
# </html>
""",
            points=15,
            order_index=1,
            difficulty="medium"
        )
        db.add(exercise2_1)
        db.commit()
        print(f"Created 1 exercise for Lesson 2")
        
        # Lesson 3: Forms and Request Handling
        lesson3_content = """# Forms and Request Handling in Flask

## The Request Object

Flask's `request` object contains information about the current HTTP request:

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/form', methods=['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        return f'Hello {name}, your email is {email}'
    
    return render_template('form.html')
```

## Creating HTML Forms

```html
<form method="POST">
    <div>
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
    </div>
    
    <div>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required>
    </div>
    
    <button type="submit">Send Message</button>
</form>
```

## Form Validation

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if errors:
            return render_template('register.html', errors=errors)
        
        return 'Registration successful!'
    
    return render_template('register.html')
```
"""
        
        lesson3 = Lesson(
            module_id=flask_module.id,
            title="Forms and Request Handling",
            content=lesson3_content,
            order_index=3,
            estimated_duration=75
        )
        db.add(lesson3)
        db.commit()
        db.refresh(lesson3)
        print(f"Created Lesson 3: {lesson3.id}")
        
        # Exercise 3.1: Contact Form
        exercise3_1 = Exercise(
            lesson_id=lesson3.id,
            title="Create a Contact Form",
            description="Build a Flask app with a contact form that accepts name, email, and message, then displays the submitted data",
            exercise_type="coding",
            starter_code="""from flask import Flask, request

app = Flask(__name__)

# Create a route that handles both GET and POST for '/contact'
# GET: Display the form
# POST: Process form data and show confirmation


if __name__ == '__main__':
    app.run(debug=True)
""",
            solution_code="""from flask import Flask, request

app = Flask(__name__)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        return f'''
        <h1>Thank you, {name}!</h1>
        <p>We received your message:</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Message:</strong> {message}</p>
        '''
    
    return '''
    <form method="POST">
        <p>Name: <input type="text" name="name" required></p>
        <p>Email: <input type="email" name="email" required></p>
        <p>Message: <textarea name="message" required></textarea></p>
        <p><input type="submit" value="Send"></p>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
""",
            points=20,
            order_index=1,
            difficulty="medium"
        )
        db.add(exercise3_1)
        db.commit()
        print(f"Created 1 exercise for Lesson 3")
        
        # Lesson 4: Flask-SQLAlchemy Integration
        lesson4_content = """# Flask-SQLAlchemy Integration

## Installation

```bash
pip install Flask-SQLAlchemy
```

## Basic Setup

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

## Creating Models

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

## Database Operations

### Creating Tables
```python
with app.app_context():
    db.create_all()
```

### Adding Data
```python
@app.route('/add_user')
def add_user():
    user = User(username='john_doe', email='john@example.com')
    db.session.add(user)
    db.session.commit()
    return f'User {user.username} created!'
```

### Querying Data
```python
@app.route('/users')
def list_users():
    users = User.query.all()
    return '<br>'.join([f'{user.username}: {user.email}' for user in users])
```
"""
        
        lesson4 = Lesson(
            module_id=flask_module.id,
            title="Flask-SQLAlchemy Integration",
            content=lesson4_content,
            order_index=4,
            estimated_duration=90
        )
        db.add(lesson4)
        db.commit()
        db.refresh(lesson4)
        print(f"Created Lesson 4: {lesson4.id}")
        
        # Exercise 4.1: Simple Blog with Database
        exercise4_1 = Exercise(
            lesson_id=lesson4.id,
            title="Create a Simple Blog with Database",
            description="Build a Flask app with SQLAlchemy that allows creating and displaying blog posts",
            exercise_type="coding",
            starter_code="""from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create a Post model with id, title, content, and created_at fields


# Create a route to display all posts


# Create a route to add new posts


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
""",
            solution_code="""from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return '<br>'.join([f'<h3>{post.title}</h3><p>{post.content}</p>' for post in posts])

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return '''
    <form method="POST">
        <p>Title: <input type="text" name="title" required></p>
        <p>Content: <textarea name="content" required></textarea></p>
        <p><input type="submit" value="Create Post"></p>
    </form>
    '''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
""",
            points=25,
            order_index=1,
            difficulty="medium"
        )
        db.add(exercise4_1)
        db.commit()
        print(f"Created 1 exercise for Lesson 4")
        
        print(f"Successfully created Flask Basics content with 4 lessons and 5 exercises")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating Flask basics content: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_flask_basics_content()