from helper import editor_required
from models import User, SetModel, BrandModel
from flask_login import login_required, current_user, login_user, logout_user
from flask import render_template, request, redirect, url_for
from sqlalchemy import func
from collections import defaultdict
import random

"""
Frontend routes
"""

def count_sets(sets):
    brand_counts = defaultdict(int)

    for set_ in sets:
        if set_.brand:
            brand_counts[set_.brand.name] += 1

    return dict(brand_counts)

def register_routes(app, db, bcrypt):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        sets = SetModel.query.all()
        brands = BrandModel.query.all()
        random.shuffle(sets)
        featured_sets = sets[:3]

        return render_template('home.html', sets=featured_sets, brands=brands)

    @app.route('/sets')
    def list_sets():
        sets = SetModel.query.all()
        brands = BrandModel.query.all()

        brand_filter = request.args.get("brand")
        print(brand_filter)

        if brand_filter:
            sets = SetModel.query.join(BrandModel).filter(func.lower(BrandModel.name) == brand_filter.lower()).all()
        else:
            sets = SetModel.query.all()
            
        return render_template('sets.html', sets=sets, brands=brands, brand_filter=brand_filter)

    @app.route('/inventory', methods=['GET', 'POST'])
    @login_required
    def inventory():
        sets = current_user.owned_sets
        brands = count_sets(sets)
        print(len(sets))
        print(str(sets[0]))
        brand_filter = request.args.get("brand")

        if brand_filter:
            sets = [set for set in sets if set.brand.name.lower() == brand_filter.lower()]

        return render_template('inventory.html', sets=sets, brands=brands, brand_filter=brand_filter)

    @app.route('/editor_home', methods=['GET', 'POST'])
    @editor_required
    def editor_home():
        #return redirect(url_for('set_editor')) 
        sets = SetModel.query.all()
        brands = BrandModel.query.all()
        return render_template('editor_home.html', sets=sets, brands=brands)
    

    @app.route('/set_editor', methods=['GET'])
    @app.route('/set_editor/<string:set_id>', methods=['GET'])
    @editor_required
    def set_editor(set_id=None):
        set_data = None
        if set_id:
            set_data = SetModel.query.get(set_id) # it is sid!
            print(set_data)
        return render_template("set_editor.html", set_data=set_data)

    @app.route('/brand_editor', methods=['GET'])
    @app.route('/brand_editor/<string:bid>', methods=['GET'])
    @editor_required
    def brand_editor(bid=None):
        brand_data = None
        if bid:
            brand_data = BrandModel.query.get(bid) # primary get
            print(brand_data)
        return render_template("brand_editor.html", brand_data=brand_data)



    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()
            print(user.password)

            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return 'Failed!'

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # we dont store the password in the db we hash it!
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(username=username, password=hashed_password)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('home'))
        
    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        # this functions just logs in the user
        logout_user()
        return redirect(url_for('login'))
    
    
    @app.route('/add_set_to_user', methods=['POST'])
    def add_set_to_user():
        set_id = request.form.get('set_id')
        lego_set = SetModel.query.get(set_id)

        current_user.owned_sets.append(lego_set)
        db.session.commit()

        return redirect(request.referrer or url_for('home'))

    @app.route('/remove_set_from_user', methods=['POST'])
    def remove_set_from_user():
        set_id = request.form.get('set_id')
        lego_set = SetModel.query.get(set_id)

        if lego_set and lego_set in current_user.owned_sets:
            current_user.owned_sets.remove(lego_set)
            db.session.commit()

        return redirect(request.referrer or url_for('home'))
    

    @app.context_processor
    def utility_processor():
        def is_active(page_name):
            return 'active' if page_name == request.endpoint else ''
        
        def is_current(page_name):
            return 'page' if page_name == request.endpoint else False
        
        def is_selected_brand(current, selected):
            if not selected and current == "":  # for the "All brands" button
                return "btn-primary"
            elif current == selected:
                return "btn-primary"
            else:
                return "btn-outline-primary"
            
        def total_pieces_owned():
            return sum(set.pieces for set in current_user.owned_sets if set.pieces)
        
        return dict(is_active=is_active, is_current=is_current, is_selected_brand=is_selected_brand, total_pieces_owned=total_pieces_owned)
