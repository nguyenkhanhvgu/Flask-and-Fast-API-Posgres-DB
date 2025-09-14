#!/usr/bin/env python3
"""
Seed script for Flask Basics tutorial content.
This script creates the Flask fundamentals learning module with lessons and exercises.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, LearningModule, Lesson, Exercise, ExerciseTestCase, ExerciseHint
import uuid

# Use the configured database (PostgreSQL in Docker)
from app.database import SessionLocal, engine
from app.models import Base
from sqlalchemy import text

# Test the connection
try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    print("Using configured PostgreSQL database")
except Exception as e:
    print(f"Database connection error: {e}")
    raise


def create_flask_basics_content():
    """Create Flask basics tutorial content."""
    db = SessionLocal()
    
    try:
        # Check if Flask Basics module already exists
        existing_module = db.query(LearningModule).filter(
            LearningModule.name == "Flask Basics",
            LearningModule.technology == "flask"
        ).first()
        
        if existing_module:
            print(f"Flask Basics module already exists: {existing_module.id}")
            return
        
        # Create Flask Basics Learning Module
        flask_module = LearningModule(
            name="Flask Basics",
            description="Learn Flask web framework fundamentals including routing, templates, forms, and database integration",
            technology="flask",
            difficulty_level="beginner",
            order_index=1,
            estimated_duration=240  # 4 hours
        )
        db.add(flask_module)
        db.flush()  # Flush to get the ID without committing
        db.refresh(flask_module)
        
        print(f"Created Flask Basics module: {flask_module.id}")
        
        # Lesson 1: Introduction to Flask and Basic Routing
        lesson1 = Lesson(
            module_id=flask_module.id,
            title="Introduction to Flask and Basic Routing",
            content="""# Introduction to Flask and Basic Routing

## What is Flask?

Flask is a lightweight and flexible Python web framework that provides the basic tools and libraries to build web applications. It's designed to be simple and easy to use, making it perfect for beginners learning web development.

## Key Features of Flask

- **Lightweight**: Minimal core with extensions for additional functionality
- **Flexible**: No rigid project structure requirements
- **Pythonic**: Uses Python conventions and idioms
- **Extensible**: Rich ecosystem of extensions

## Installing Flask

```bash
pip install Flask
```

## Your First Flask Application

Let's create a simple "Hello World" Flask application:

```python
from flask import Flask

# Create Flask application instance
app = Flask(__name__)

# Define a route
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
```

## Understanding Routes

Routes in Flask define URL patterns and map them to Python functions. The `@app.route()` decorator is used to bind a function to a URL.

### Basic Route Examples

```python
@app.route('/')
def home():
    return 'Home Page'

@app.route('/about')
def about():
    return 'About Page'

@app.route('/contact')
def contact():
    return 'Contact Page'
```

### Dynamic Routes

Flask supports dynamic routes with variable parts:

```python
@app.route('/user/<username>')
def user_profile(username):
    return f'Hello, {username}!'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post ID: {post_id}'
```

### HTTP Methods

By default, routes only respond to GET requests. You can specify other methods:

```python
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        return 'Form submitted!'
    return 'Submit form here'
```

## Running Your Flask App

1. Save your code in a file (e.g., `app.py`)
2. Run: `python app.py`
3. Open your browser to `http://127.0.0.1:5000`

## Development Mode

Enable debug mode for automatic reloading and better error messages:

```python
app.run(debug=True)
```

Or set the environment variable:
```bash
export FLASK_ENV=development
flask run
```
""",
            order_index=1,
            estimated_duration=45
        )
        db.add(lesson1)
        db.flush()
        db.refresh(lesson1)
        
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


# Run the application (uncomment the lines below when ready to test)
# if __name__ == '__main__':
#     app.run(debug=True)
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
        db.flush()
        db.refresh(exercise1_1)
        
        # Add hints for exercise 1.1
        hints1_1 = [
            ExerciseHint(
                exercise_id=exercise1_1.id,
                hint_text="Start by creating a Flask instance: app = Flask(__name__)",
                order_index=1
            ),
            ExerciseHint(
                exercise_id=exercise1_1.id,
                hint_text="Use the @app.route('/') decorator to define the home route",
                order_index=2
            ),
            ExerciseHint(
                exercise_id=exercise1_1.id,
                hint_text="The function should return the string 'Welcome to Flask!'",
                order_index=3
            )
        ]
        for hint in hints1_1:
            db.add(hint)
        
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
        db.flush()
        db.refresh(exercise1_2)
        
        print(f"Created Lesson 1: {lesson1.id} with 2 exercises")
        
        # Lesson 2: Templates and Static Files
        lesson2 = Lesson(
            module_id=flask_module.id,
            title="Templates and Static Files",
            content="""# Templates and Static Files in Flask

## Introduction to Templates

Templates allow you to separate your HTML from your Python code, making your application more maintainable and following the MVC (Model-View-Controller) pattern.

Flask uses the Jinja2 templating engine, which provides powerful features like template inheritance, variables, and control structures.

## Setting Up Templates

Flask looks for templates in a `templates` folder by default:

```
your_project/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── about.html
└── static/
    ├── css/
    ├── js/
    └── images/
```

## Basic Template Usage

### Python Code (app.py)
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='Home Page')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', username=name)
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
    <p>This is the home page.</p>
</body>
</html>
```

## Template Variables

Pass data from your routes to templates:

```python
@app.route('/profile/<username>')
def profile(username):
    user_data = {
        'name': username,
        'email': f'{username}@example.com',
        'posts': 42
    }
    return render_template('profile.html', user=user_data)
```

```html
<!-- templates/profile.html -->
<h1>{{ user.name }}'s Profile</h1>
<p>Email: {{ user.email }}</p>
<p>Posts: {{ user.posts }}</p>
```

## Template Inheritance

Create a base template for consistent layout:

### Base Template (templates/base.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Flask App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('home') }}">Home</a>
        <a href="{{ url_for('about') }}">About</a>
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### Child Template (templates/home.html)
```html
{% extends "base.html" %}

{% block title %}Home - Flask App{% endblock %}

{% block content %}
    <h1>Welcome to Flask!</h1>
    <p>This is the home page content.</p>
{% endblock %}
```

## Static Files

Static files (CSS, JavaScript, images) go in the `static` folder:

### Linking Static Files
```html
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>

<!-- Images -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

## Control Structures in Templates

### Conditionals
```html
{% if user.is_authenticated %}
    <p>Welcome back, {{ user.name }}!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}
```

### Loops
```html
<ul>
{% for post in posts %}
    <li>{{ post.title }} - {{ post.date }}</li>
{% endfor %}
</ul>
```

## Template Filters

Jinja2 provides built-in filters to modify variables:

```html
<p>{{ message|upper }}</p>  <!-- Convert to uppercase -->
<p>{{ date|strftime('%Y-%m-%d') }}</p>  <!-- Format date -->
<p>{{ content|truncate(100) }}</p>  <!-- Truncate text -->
```

## Best Practices

1. **Use template inheritance** for consistent layouts
2. **Keep logic in Python**, not templates
3. **Use url_for()** for generating URLs
4. **Organize static files** in appropriate subdirectories
5. **Use descriptive template names**
""",
            order_index=2,
            estimated_duration=60
        )
        db.add(lesson2)
        db.flush()
        db.refresh(lesson2)
        
        # Exercise 2.1: Basic Template
        exercise2_1 = Exercise(
            lesson_id=lesson2.id,
            title="Create a Basic Template",
            description="Create a Flask app that uses a template to display a welcome message with the user's name",
            exercise_type="coding",
            starter_code="""from flask import Flask, render_template

app = Flask(__name__)

# Create a route that renders a template with a name variable


# Template content should be in templates/welcome.html
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
        db.flush()
        db.refresh(exercise2_1)
        
        print(f"Created Lesson 2: {lesson2.id} with 1 exercise")
        
        # Lesson 3: Forms and Request Handling
        lesson3 = Lesson(
            module_id=flask_module.id,
            title="Forms and Request Handling",
            content="""# Forms and Request Handling in Flask

## Introduction to Forms

Web forms are essential for user interaction. Flask provides tools to handle form data, validate input, and process user submissions.

## The Request Object

Flask's `request` object contains all the information about the current HTTP request:

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/form', methods=['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        return f'Hello {name}, your email is {email}'
    
    # Show the form
    return render_template('form.html')
```

## Creating HTML Forms

### Basic Form Template (templates/form.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Contact Form</title>
</head>
<body>
    <h1>Contact Us</h1>
    <form method="POST">
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
        </div>
        
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div>
            <label for="message">Message:</label>
            <textarea id="message" name="message" rows="4" required></textarea>
        </div>
        
        <button type="submit">Send Message</button>
    </form>
</body>
</html>
```

## Handling Different HTTP Methods

```python
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Here you would typically save to database or send email
        return render_template('success.html', name=name)
    
    # GET request - show the form
    return render_template('contact.html')
```

## Form Validation

### Basic Validation
```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        errors = []
        
        # Validation
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            return render_template('register.html', errors=errors)
        
        # Registration successful
        return redirect(url_for('login'))
    
    return render_template('register.html')
```

## File Uploads

```python
from werkzeug.utils import secure_filename
import os

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file selected'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No file selected'
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f'File {filename} uploaded successfully'
    
    return render_template('upload.html')
```

## Request Data Types

### Form Data
```python
# POST form data
name = request.form['name']
name = request.form.get('name', 'Default')  # With default value
```

### Query Parameters
```python
# GET parameters (?page=1&limit=10)
page = request.args.get('page', 1, type=int)
limit = request.args.get('limit', 10, type=int)
```

### JSON Data
```python
@app.route('/api/data', methods=['POST'])
def api_data():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        return {'message': f'Hello {name}'}
    return {'error': 'Invalid JSON'}, 400
```

## Flash Messages

Display temporary messages to users:

```python
from flask import flash, redirect, url_for

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')
```

### Displaying Flash Messages in Templates
```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

## CSRF Protection

For production applications, always protect against CSRF attacks:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'your-secret-key'
```

## Best Practices

1. **Always validate user input** on the server side
2. **Use HTTPS** for sensitive forms
3. **Implement CSRF protection** for state-changing operations
4. **Sanitize file uploads** and limit file types
5. **Use flash messages** for user feedback
6. **Handle errors gracefully** with proper error pages
""",
            order_index=3,
            estimated_duration=75
        )
        db.add(lesson3)
        db.flush()
        db.refresh(lesson3)
        
        # Exercise 3.1: Contact Form
        exercise3_1 = Exercise(
            lesson_id=lesson3.id,
            title="Create a Contact Form",
            description="Build a Flask app with a contact form that accepts name, email, and message, then displays the submitted data",
            exercise_type="coding",
            starter_code="""from flask import Flask, request, render_template

app = Flask(__name__)

# Create a route that handles both GET and POST for '/contact'
# GET: Display the form
# POST: Process form data and show confirmation


if __name__ == '__main__':
    app.run(debug=True)
""",
            solution_code="""from flask import Flask, request, render_template

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
        db.flush()
        db.refresh(exercise3_1)
        
        print(f"Created Lesson 3: {lesson3.id} with 1 exercise")
        
        # Lesson 4: Flask-SQLAlchemy Integration
        lesson4 = Lesson(
            module_id=flask_module.id,
            title="Flask-SQLAlchemy Integration",
            content="""# Flask-SQLAlchemy Integration

## Introduction to Flask-SQLAlchemy

Flask-SQLAlchemy is an extension that adds SQLAlchemy support to Flask applications. It simplifies database operations and provides an Object-Relational Mapping (ORM) layer.

## Installation

```bash
pip install Flask-SQLAlchemy
```

## Basic Setup

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
```

## Creating Models

Models represent database tables as Python classes:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
```

## Database Operations

### Creating Tables
```python
# Create all tables
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

@app.route('/user/<username>')
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return f'User: {user.username}, Email: {user.email}'
```

### Updating Data
```python
@app.route('/update_user/<int:user_id>')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.email = 'newemail@example.com'
    db.session.commit()
    return f'User {user.username} updated!'
```

### Deleting Data
```python
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return f'User deleted!'
```

## Advanced Queries

### Filtering
```python
# Filter by condition
active_users = User.query.filter(User.is_active == True).all()

# Multiple conditions
recent_posts = Post.query.filter(
    Post.created_at > datetime(2023, 1, 1),
    Post.title.contains('Flask')
).all()
```

### Ordering
```python
# Order by creation date
recent_users = User.query.order_by(User.created_at.desc()).all()

# Multiple ordering
posts = Post.query.order_by(Post.created_at.desc(), Post.title).all()
```

### Pagination
```python
@app.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(
        page=page, 
        per_page=5, 
        error_out=False
    )
    return render_template('posts.html', posts=posts)
```

## Relationships

### One-to-Many
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

### Many-to-Many
```python
# Association table
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=user_roles, backref='users')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
```

## Forms with Database Integration

```python
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = 1  # In real app, get from session
        
        post = Post(title=title, content=content, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('posts'))
    
    return render_template('create_post.html')
```

## Database Migrations

For production applications, use Flask-Migrate:

```bash
pip install Flask-Migrate
```

```python
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## Best Practices

1. **Use migrations** for schema changes in production
2. **Handle database errors** with try-catch blocks
3. **Use transactions** for related operations
4. **Index frequently queried columns**
5. **Validate data** before database operations
6. **Use connection pooling** for better performance
7. **Close database connections** properly

## Complete Example

```python
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        
        flash('Post created!', 'success')
        return redirect(url_for('index'))
    
    return render_template('create.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```
""",
            order_index=4,
            estimated_duration=90
        )
        db.add(lesson4)
        db.flush()
        db.refresh(lesson4)
        
        # Exercise 4.1: Simple Blog with Database
        exercise4_1 = Exercise(
            lesson_id=lesson4.id,
            title="Create a Simple Blog with Database",
            description="Build a Flask app with SQLAlchemy that allows creating and displaying blog posts",
            exercise_type="coding",
            starter_code="""from flask import Flask, request, render_template, redirect, url_for
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
            solution_code="""from flask import Flask, request, render_template, redirect, url_for
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
        db.flush()
        db.refresh(exercise4_1)
        
        print(f"Created Lesson 4: {lesson4.id} with 1 exercise")
        
        db.commit()
        print(f"Successfully created Flask Basics content with {len([lesson1, lesson2, lesson3, lesson4])} lessons")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating Flask basics content: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_flask_basics_content()