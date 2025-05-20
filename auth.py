from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from models import User, Role
from __init__ import db
from flask_login import login_user, login_required, logout_user
from models import db, CartItem

# Defines the authentication blueprint
auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    # Handles user login functionality
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        # Checks if the user exists
        if user:
            # Verifies the password against the hashed password stored in the database
            if check_password_hash(user.password, password):
                login_user(user, remember=True)  # Logs in the user and remembers session
                flash('Logged in successfully!', category='success')
                
                # Retrieves the user's cart items from the database
                user_cart_items = CartItem.query.filter_by(user_id=user.id).all()
                
                # Ensures the session has a cart and populates it with stored items
                if 'cart' not in session:
                    session['cart'] = {}
                for item in user_cart_items:
                    session['cart'][str(item.product_id)] = item.quantity
                
                # Checks if the user has an admin role and redirects accordingly
                role_name = 'Admin'
                is_admin = any(role.name == role_name for role in user.roles)
                if is_admin:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('home.homepage'))
            else:
                flash('Incorrect Password, try again.', category='error')
        else:
            flash('User does not exist', category='error')
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handles user registration functionality
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        
        # Validates the user input
        if len(email) > 7:
            if user:
                flash('Email already exists.', category='error')
            elif len(first_name) < 2:
                flash('First Name must be greater than 1 character', category='error')
            elif password1 != password2:
                flash('Passwords do not match', category='error')
            elif len(password1) < 8:
                flash('Password must be at least 8 characters', category='error')
            else:
                # Creates a new user with a hashed password
                flash('Account Created!!', category='success')
                new_user = User(email=email, first_name=first_name, last_name=last_name, 
                                password=generate_password_hash(password1, method="pbkdf2:sha256"))
                
                # Assigns the default role of 'Customer'
                role = Role.query.filter_by(name='Customer').first()
                new_user.roles.append(role)
                
                # Adds the new user to the database
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)  # Logs in the newly registered user
                return redirect(url_for('home.homepage'))
        else:
            flash('Email does not exist', category='error')
    
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    # Handles user logout by clearing session data and redirecting to login
    session.pop('cart', None)  # Removes cart from session
    logout_user()
    return redirect(url_for('auth.login'))
