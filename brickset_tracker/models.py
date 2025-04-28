from flask_login import UserMixin
from app import db

# Association tables
user_sets = db.Table('user_sets',
    db.Column('user_id', db.Integer, db.ForeignKey('users.uid'), primary_key=True),
    db.Column('set_id', db.Integer, db.ForeignKey('sets.sid'), primary_key=True)
)

sets_tags = db.Table('sets_tags',
    db.Column('set_id', db.Integer, db.ForeignKey('sets.sid'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')

    owned_sets = db.relationship('SetModel', secondary=user_sets, backref='owners', lazy=True)
    
    def __repr__(self):
        return f'<User: {self.username}, Role: {self.role}>'
    
    def get_id(self):
        return self.uid

class TagModel(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
   
class SetModel(db.Model):
    __tablename__ = 'sets'
    sid = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.String(100), nullable=False)  # unique
    name = db.Column(db.String(100), nullable=False)
    pieces = db.Column(db.Integer)
    year = db.Column(db.Integer)
    image_url = db.Column(db.String(200)) # /static/images/set_image.jpg
    description = db.Column(db.Text)
    
    instruction_url = db.Column(db.String(300))
    minifigures = db.Column(db.Integer)


    # 1 to many
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.bid'), nullable=False)
    # many to many
    tags = db.relationship('TagModel', secondary=sets_tags, backref='sets', lazy=True)
    
    # later store who added the set?
    # created_by = db.Column(db.Integer, db.ForeignKey('users.uid'))

class BrandModel(db.Model):
    __tablename__ = 'brands'
    bid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

    # this is the owner
    # backref puts a new column on the child
    sets = db.relationship('SetModel', backref='brand', lazy=True)
