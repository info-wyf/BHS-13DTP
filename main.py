# Import required Flask and related modules
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime
import logging

# Configure logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask application
app = Flask(__name__)

# Set configuration variables
app.config['SECRET_KEY'] = 'your_secure_secret_key'  # Secure key for session and form security
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza.db'  # SQLite database path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
app.config['DEBUG'] = True  # Enable debug mode for development

# Initialize SQLAlchemy for database operations
db = SQLAlchemy(app)

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# Define User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Store hashed passwords in production

# Define Order model for the Orders table
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Customer name
    topping = db.Column(db.String(100), nullable=False)  # Pizza topping
    sauce = db.Column(db.String(100), nullable=False)  # Pizza sauce
    extras = db.Column(db.String(200))  # Optional extras
    instructions = db.Column(db.Text)  # Special instructions
    update_time = db.Column(db.DateTime, default=datetime.utcnow)  # Order timestamp

# Define OrderForm for handling order submissions
class OrderForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired(), Length(min=1, max=100)])
    topping = StringField('Topping', validators=[DataRequired(), Length(min=1, max=100)])
    sauce = StringField('Sauce', validators=[DataRequired(), Length(min=1, max=100)])
    extras = StringField('Extras', validators=[Length(max=200)])
    instructions = TextAreaField('Special Instructions', validators=[Length(max=500)])
    submit = SubmitField('Place Order')

# Define LoginForm for user authentication
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=50)])
    password = StringField('Password', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Login')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')  # Render home page template

# Order route for creating new orders
@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    form = OrderForm()
    if form.validate_on_submit():
        try:
            # Create new order instance
            new_order = Order(
                name=form.name.data,
                topping=form.topping.data,
                sauce=form.sauce.data,
                extras=form.extras.data,
                instructions=form.instructions.data
            )
            db.session.add(new_order)
            db.session.commit()
            flash('Order placed successfully!', 'success')
            logging.info(f'Order placed by {form.name.data}')
            return redirect(url_for('order_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error placing order: {str(e)}', 'error')
            logging.error(f'Order placement failed: {str(e)}')
    return render_template('order.html', form=form)

# Order list route for viewing all orders
@app.route('/order_list')
@login_required
def order_list():
    try:
        orders = Order.query.all()  # Retrieve all orders
        return render_template('order_list.html', orders=orders)
    except Exception as e:
        flash(f'Error retrieving orders: {str(e)}', 'error')
        logging.error(f'Order list retrieval failed: {str(e)}')
        return render_template('order_list.html', orders=[])

# Login route for user authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # Use proper hashing in production
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Initialize database and run application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)