from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'python123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bakery.db'
db = SQLAlchemy(app)

# Define the Menu Item model
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<MenuItem {self.name}>"

# Define the Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    items = db.Column(db.String(500), nullable=False)  # List of items (JSON or simple text)
    total_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Order {self.username} - {self.total_price}>"

# Home page, showing a welcome message or bakery info
@app.route('/')
def home():
    return render_template('index.html')

# About page to describe the bakery
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page for customer support or inquiries
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Menu page, showing all available items
@app.route('/menu')
def menu():
    items = MenuItem.query.all()  # Fetch all items from the menu
    return render_template('menu.html', items=items)

# Checkout page, where customers can review their selected items
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        username = request.form['username']
        item_ids = request.form.getlist('item_ids')  # Get selected item IDs
        selected_items = MenuItem.query.filter(MenuItem.id.in_(item_ids)).all()

        total_price = sum(item.price for item in selected_items)
        order_items = ', '.join([item.name for item in selected_items])

        # Create a new order record in the database
        new_order = Order(username=username, items=order_items, total_price=total_price)
        db.session.add(new_order)
        db.session.commit()

        flash(f"Order placed successfully! Total: ${total_price:.2f}", 'success')
        return redirect(url_for('bill', order_id=new_order.id))

    items = MenuItem.query.all()
    return render_template('checkout.html', items=items)

# Bill page, showing the details of the order placed
@app.route('/bill/<int:order_id>')
def bill(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('bill.html', order=order)

# Register a menu item (Admin functionality)
@app.route('/add_menu_item', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        new_item = MenuItem(name=name, price=price)
        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('menu'))
    return render_template('add_menu_item.html')

# Create the database and tables if not already created
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
