from flask import render_template, request, redirect, url_for, session, flash, Blueprint
import json
from flask_login import login_required, current_user
from models import CartItem, db, Order

home = Blueprint('home', __name__)

# Load product data from JSON file
with open('data/products.json') as f:
    products = json.load(f)

def save_products(products):
    """Save updated products back to JSON file."""
    with open('data/products.json', 'w') as f:
        json.dump(products, f, indent=4)

def get_cart():
    cart = session.get('cart', {})
    cart_items = [
        {
            'product': next((p for p in products if p['id'] == int(product_id)), None),
            'quantity': quantity
        }
        for product_id, quantity in cart.items()
    ]
    #retrieves the items in the cart for loading
    return cart_items

@home.route('/')
@login_required
def homepage():
    return render_template('home.html', products=products)

@home.route('/product/<int:product_id>')
def product_detail(product_id):
    #Displays details for a single product, fed by the HTML
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash("Product not found", category="error")
        return redirect(url_for('home.homepage'))
    
    return render_template('products.html', product=product)

@home.route('/cart')
@login_required
def view_cart():
    cart_items = get_cart()
    #Retrieves the items in the cart, then calculates and displays the total price
    total = sum(item['product']['price'] * item['quantity'] for item in cart_items if item['product'] is not None)
    return render_template('cart.html', cart_items=cart_items, total = total)

@home.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if not product:
        flash("Product not found", category="error")
        return redirect(url_for('home.homepage'))

    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    session.modified = True
    #adds the specific item to the cart, then writes it to the respective part of the database
    if current_user.is_authenticated:
        cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += 1
        else:
            new_cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=1)
            db.session.add(new_cart_item)
        db.session.commit()

    

    flash("Item added to cart!", category="success")
    return redirect(url_for('home.view_cart'))

@home.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    session.pop('cart', None)  # Clear session cart
    CartItem.query.filter_by(user_id=current_user.id).delete()  # Remove from database
    db.session.commit()
    
    flash("Cart cleared successfully!", category="success")
    return redirect(url_for('home.view_cart'))

@home.route('/checkout', methods=['POST','GET'])
@login_required
def checkout():
    cart_items = get_cart()
    total = sum(item['product']['price'] * int(item['quantity']) for item in cart_items)

    return render_template('checkout.html', cart_items = cart_items, total = total)

@home.route('/process_checkout', methods=['GET','POST'])
@login_required
def process_checkout():
    cart_items = get_cart()
    total = sum(item['product']['price'] * item['quantity'] for item in cart_items)
    payment_method = request.form.get('payment')
    new_order = Order(user_id = current_user.id, total_price = total, payment_method = payment_method)
    db.session.add(new_order)
    db.session.commit()
    flash('Order placed successfully!', category='success')
    return redirect(url_for('home.homepage'))
