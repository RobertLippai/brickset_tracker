from flask import abort, request
from flask_restful import Resource, marshal, marshal_with, fields, reqparse
from helper import api_editor_required
from models import BrandModel, SetModel
from app import db
from sqlalchemy import func

"""

This file will contain API endpoints.

"""

"""
    set_id = db.Column(db.String(100), nullable=False) 
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    pieces = db.Column(db.Integer)
    year = db.Column(db.Integer)
    image_url = db.Column(db.String(200))
"""


# key value
setFields = {
    'set_id': fields.String,
    'name': fields.String,
    'brand.name': fields.String
}

setFieldsDetail = {
    'set_id': fields.String,
    'name': fields.String,
    'brand.name': fields.String,
    'pieces': fields.Integer,
    'year': fields.Integer
}

set_args_create = reqparse.RequestParser()
set_args_create.add_argument('set_id', type=str, required=True, help="Set ID cannot be blank!")
set_args_create.add_argument('name', type=str, required=True, help="Set Name cannot be blank!")
set_args_create.add_argument('brand', type=str, required=True, help="Set Brand cannot be blank!")
set_args_create.add_argument('pieces', type=str, help="Number of pieces is optional.")
set_args_create.add_argument('year', type=str, help="Release year is optional.")

brandFields = {
    'bid': fields.String,
    'name': fields.String
}

setSummaryFields = {
    'set_id': fields.String,
    'name': fields.String,
}

brandFieldsDetail = {
    'bid': fields.String,
    'name': fields.String,
    'description': fields.String,
    'sets' : fields.List(fields.Nested(setSummaryFields))
}

brand_args_create = reqparse.RequestParser()
brand_args_create.add_argument('name', type=str, required=True, help="Brand Name cannot be blank!")
brand_args_create.add_argument('description', type=str, help="Description is optional!")

brand_args_update = reqparse.RequestParser()
brand_args_update.add_argument('name', type=str, help="Brand is optional!")
brand_args_update.add_argument('description', type=str, help="Description is optional!")


class Brands(Resource):
    @marshal_with(brandFields)
    def get(self):
        brands = BrandModel.query.all()
        return brands, 200
    
    @marshal_with(brandFields)
    #@api_editor_required
    def post(self):
        # if this doesnt parse correctly it will send back a response
        args = brand_args_create.parse_args()

        # creating a set from arguments
        brand = BrandModel(name=args['name'])

        if args['description'] is not None:
            brand.description = args['description']

        db.session.add(brand) # add to db
        db.session.commit()

        brands = BrandModel.query.all()
        return brands, 201 # 201 means created

class Brand(Resource):
    @marshal_with(brandFieldsDetail)
    def get(self, id):
        brand  = BrandModel.query.filter(BrandModel.bid == id).first()

        print(brand.sets)
        if not brand:
            abort(404, 'Brand not found!')

        return brand, 200

    @marshal_with(brandFieldsDetail)
    #@api_editor_required
    def put(self, id):
        args = brand_args_update.parse_args() # this is related to line 24-26
        print(args)
        brand = BrandModel.query.filter(BrandModel.bid == id).first()

        if not brand:
            abort(404, "Brand not found") # 404 not found

        if args['name'] is not None:
            brand.name = args['name']
        if args['description'] is not None:
            brand.description = args['description']
        
        db.session.commit()

        return brand, 200
    

    @marshal_with(brandFields)
    #@api_editor_required
    def delete(self, id):
        brand = BrandModel.query.filter_by(bid=id).first()

        if not brand:
            abort(404, "Brand not found") # 404 not found

        db.session.delete(brand)
        db.session.commit()

        brands = BrandModel.query.all()
        
        return marshal(brands, brandFields), 200          

class BrickSets(Resource):
    @marshal_with(setFields)
    def get(self):
        sets = SetModel.query.all()
        return sets, 200
    
    @marshal_with(setFields)  
    @api_editor_required 
    def post(self):
        # if this doesnt parse correctly it will send back a response
        args = set_args_create.parse_args()
        brand = BrandModel.query.filter(func.lower(BrandModel.name) == args['brand'].lower()).first()
        if not brand:
            abort(400, "Brand not found!")

        # creating a set from arguments
        set = SetModel(set_id=args['set_id'], name=args['name'], brand_id=brand.bid)

        if args['pieces'] is not None:
            set.pieces = args['pieces']
        if args['year'] is not None:
            set.year = args['year']

        db.session.add(set) # add to db
        db.session.commit()

        sets = SetModel.query.all()
        return sets, 201 # 201 means created


# Individual Brick Set

set_args_update = reqparse.RequestParser()
set_args_update.add_argument('set_id', type=str, help="set_id is optional")
set_args_update.add_argument('name', type=str, help="Name is optinal")
set_args_update.add_argument('brand', type=str, help="Brand is optonal")
set_args_update.add_argument('pieces', type=int, help="Number of pieces is optional")
set_args_update.add_argument('year', type=int, help="Release year is optional")

class BrickSet(Resource):    
    @marshal_with(setFieldsDetail)
    def get(self, id):
        set = SetModel.query.filter(SetModel.sid == id).first()

        if not set:
            abort(404, "Set not found") # 404 not found

        return set, 200

    @marshal_with(setFieldsDetail)
    #@api_editor_required
    def put(self, id):
        args = set_args_update.parse_args() # this is related to line 24-26
        print(args)
        set = SetModel.query.filter(SetModel.sid == id).first()
        print(set.set_id)

        if not set:
            abort(404, "Set not found") # 404 not found


        if args['set_id'] is not None:
            set.set_id = args['set_id']
        if args['name'] is not None:
            set.name = args['name']
        if args['brand'] is not None:
            brand = BrandModel.query.filter(func.lower(BrandModel.name) == args['brand'].lower()).first()
            if not brand:
                abort(400, "Brand not found!")
            set.brand_id = brand.bid
        if args['pieces'] is not None:
            set.pieces = args['pieces']
        if args['year'] is not None:
            set.year = args['year']
        db.session.commit()

        return set, 200

    @marshal_with(setFields)
    @api_editor_required
    def delete(self, id):
        print("method run")
        set = SetModel.query.filter_by(sid=id).first()

        if not set:
            abort(404, "Set not found") # 404 not found

        db.session.delete(set)
        db.session.commit()

        sets = SetModel.query.all()
        
        return marshal(sets, setFields), 200      
    

class SetSearch(Resource):
    @marshal_with(setFields)
    def get(self):
        search_term = request.args.get('q') or ''
        if not search_term:
            return {'error': 'No search term provided'}, 400

        found_sets = SetModel.query.filter(SetModel.name.ilike(f'%{search_term}%')).all()
        return found_sets