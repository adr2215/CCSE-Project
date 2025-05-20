from flask import render_template, request, redirect, url_for, flash, Blueprint, abort
from flask_login import login_required, current_user
from models import Order, db, User, Role, roles_users, CartItem
from home import products
import json
from flask import current_app
from werkzeug.utils import secure_filename
from os import path
admin = Blueprint('admin',__name__)

def is_admin():
    admin_role = Role.query.filter_by(name='Admin').first()
    if admin_role not in current_user.roles:
        return False
    else:
        return True
#For all admin functions, the is_admin function is run to check whether a user is allowed to access a page
# If not, they are given an error    


@admin.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if not is_admin():
        abort(403)
    if request.method == 'POST':
        name = request.form.get('product_name')
        description = request.form.get('product_description')
        price = request.form.get('price')
        image = request.files['image']
        #Admin can establish the name, description and price of a new product
        #As well as uploading an image to be stored locally
        if not name or not description or not price:
            #Validation to ensure all fields are filled
            flash('All fields are required!', category='error')
            return redirect(url_for('admin.add_product'))
        elif image.filename == '':
            #Validation to ensure an image is selected
            flash('No selected image!', category='error')
            return redirect(url_for('admin.add_product'))
        

        filename = secure_filename(image.filename)
        #sanitises the file name before storing it lcally, to prevent a file named ;../../../../../etc/passwd'
        #from being uploaded
        image_path = path.join(current_app.root_path, 'static', filename)
        
        image.save(image_path)

        # Create a new product
        new_product = {
            'id': max(p['id'] for p in products) + 1,  # Generate a new unique ID
            'name': name,
            'description': description,
            'price': float(price),
            'image_url': {filename}}
        
        flash('Product Added!', category='success')
        products.append(new_product)
        
        #Retrieves the produvts from the json file and adds the newly created product
        with open('data/products.json', 'w') as f:
            json.dump(products, f, indent=4)
            return redirect(url_for('admin.dashboard'))
            #then returns the user to the admin dashboard
        
    return render_template('add_product.html') 

@admin.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not is_admin(): #Role-Based Access Controls continuation
        abort(403)
    return render_template('admin_dashboard.html')

@admin.route('/home', methods = ['GET','POST'])
@login_required
def home():
    if not is_admin(): #Generates an admin-specific version of the home page
        abort(403)
    return render_template('admin_home.html', products = products)

@admin.route('/view_orders', methods = ['GET','POST'])
@login_required
def view_orders():
    if not is_admin():
        abort(403)
    orders = Order.query.all()
    #Retrieves all orders on the database in order to display them on the html page
    return render_template('view_orders.html',orders = orders)

@admin.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required 
def update_order_status(order_id):
    if not is_admin():
        abort(403)
    order = Order.query.get(order_id)
    new_status = request.form.get('status')
    #Retrieves the requested new status and ensures it is one of the valid option
    if new_status in ['Pending', 'Processing', 'Shipped', 'Delivered']:
        order.status = new_status
        db.session.commit()
        #Alters the database to the new status
        flash('Order status updated successfully.', 'success')
    else:
        flash('Invalid status update.', 'error')
    return redirect(url_for('admin.view_orders'))

@admin.route('/delete_order/<int:order_id>', methods = ['POST'])
@login_required
def delete_order(order_id):
    if not is_admin():
        abort(403)
    order = Order.query.get(order_id)
    
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully.', 'success')
    
    return redirect(url_for('admin.view_orders'))

@admin.route('/manage_users', methods = ['GET','POST'])
@login_required
def manage_users():
    if not is_admin():
        abort(403)
    users = User.query.all()
    all_roles = Role.query.all()
    return render_template('manage_users.html', users = users,all_roles = all_roles)

@admin.route('/update_role/<int:user_id>', methods = ['GET','POST'])
@login_required
def update_role(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get(user_id)
    new_role_name = request.form.get('role')
    new_role = Role.query.filter_by(name=new_role_name).first()

    db.session.execute(roles_users.delete().where(roles_users.c.user_id == user.id))  # Remove existing role
    db.session.execute(roles_users.insert().values(user_id=user.id, role_id=new_role.id))  # Assign new role
    db.session.commit()
    flash('User role updated successfully.', 'success')

    return redirect(url_for('admin.manage_users'))    

@admin.route('/delete_user/<int:user_id>', methods = ['POST'])
@login_required
def delete_user(user_id):
    if not is_admin():
        abort(403)
    user = User.query.get(user_id)

    CartItem.query.filter_by(user_id=user.id).delete()
    Order.query.filter_by(user_id=user.id).delete()
    db.session.execute(roles_users.delete().where(roles_users.c.user_id == user.id))
    #Ensures that database integrity is kept by removing data from all associated tables
    db.session.commit()  
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    
    return redirect(url_for('admin.manage_users'))



        