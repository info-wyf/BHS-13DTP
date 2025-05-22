from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField, SelectMultipleField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime

# init Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # WTForms 需要
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizza.db'  # SQLite 数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# define database model
pizza_topping = db.Table('pizza_topping',
                         db.Column('pid', db.Integer, db.ForeignKey('pizza.id'), primary_key=True),
                         db.Column('tid', db.Integer, db.ForeignKey('topping.id'), primary_key=True)
                         )


class Pizza(db.Model):
    __tablename__ = 'pizza'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    base = db.Column(db.String(50))
    toppings = db.Column(db.String(100))
    picture = db.Column(db.String(255))
    toppings_rel = db.relationship('Topping', secondary=pizza_topping, backref=db.backref('pizzas', lazy='dynamic'))


class Topping(db.Model):
    __tablename__ = 'topping'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    topping = db.Column(db.String(50), nullable=False)
    sauce = db.Column(db.String(50), nullable=False)
    extras = db.Column(db.String(100))
    instructions = db.Column(db.Text)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)


# define WTForms
class OrderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    topping = RadioField('Pizza Topping',
                         choices=[('Supreme', 'Supreme'), ('Vegetarian', 'Vegetarian'), ('Hawaiian', 'Hawaiian')],
                         validators=[DataRequired()])
    sauce = SelectField('Pizza Sauce', choices=[('Tomato', 'Tomato'), ('BBQ', 'BBQ'), ('Garlic', 'Garlic')],
                        validators=[DataRequired()])
    extras = SelectMultipleField('Optional Extras',
                                 choices=[('Extra Cheese', 'Extra Cheese'), ('Gluten Free Base', 'Gluten Free Base')])
    instructions = TextAreaField('Delivery Instructions')
    submit = SubmitField('Send my Order')


# routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/all_pizzas')
def all_pizzas():
    pizzas = Pizza.query.order_by(Pizza.name.asc()).all()
    return render_template('all_pizzas.html', pizzas=pizzas)


@app.route('/pizza/<int:id>')
def pizza(id):
    pizza = Pizza.query.get_or_404(id)
    return render_template('pizza.html', pizza=pizza)


@app.route('/order', methods=['GET', 'POST'])
def order():
    form = OrderForm()
    if form.validate_on_submit():
        name = form.name.data
        topping = form.topping.data
        sauce = form.sauce.data
        extras = ', '.join(form.extras.data) if form.extras.data else None
        instructions = form.instructions.data

        print(f"Inserting order: {name}, {topping}, {sauce}, {extras}, {instructions}")  # 调试日志
        existing_order = Order.query.filter_by(name=name).first()
        if existing_order:
            existing_order.topping = topping
            existing_order.sauce = sauce
            existing_order.extras = extras
            existing_order.instructions = instructions
            existing_order.update_time = datetime.utcnow()
        else:
            new_order = Order(name=name, topping=topping, sauce=sauce, extras=extras, instructions=instructions)
            db.session.add(new_order)
        db.session.commit()

        return render_template('confirmation.html', name=name, topping=topping, sauce=sauce, extras=extras,
                               instructions=instructions)
    return render_template('order_form.html', form=form)


@app.route('/orderList')
def orderList():
    search_query = request.args.get('search', '')
    if search_query:
        orders = Order.query.filter(Order.name.ilike(f'%{search_query}%')).order_by(Order.id.asc()).all()
    else:
        orders = Order.query.order_by(Order.id.asc()).all()
    return render_template('orders_list.html', orders=orders, search_query=search_query)


@app.route('/edit_order/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    order = Order.query.get_or_404(id)
    form = OrderForm(obj=order)
    if form.validate_on_submit():
        form.populate_obj(order)
        # sqlalchemy.exc.ProgrammingError: (sqlite3.ProgrammingError) Error binding parameter 2: type 'list' is not supported
        order.extras = ', '.join(form.extras.data)  # Convert list to string to solve the problems above
        order.update_time = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('orderList'))
    return render_template('edit_order.html', form=form, order=order)


@app.route('/delete_order/<int:id>', methods=['POST'])
def delete_order(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('orderList'))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# init database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)