from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    token = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "token": self.token
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    diameter = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    gravity = db.Column(db.String(40))
    population = db.Column(db.Integer)
    climate = db.Column(db.String(40))
    terrain = db.Column(db.String(50))
    surface_water = db.Column(db.Integer)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
        }
    

class Characters(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    height = db.Column(db.Integer)
    mass = db.Column(db.Integer)
    hair_color = db.Column(db.String(30))
    skin_color = db.Column(db.String(30))
    eye_color = db.Column(db.String(30))
    birth_year = db.Column(db.String(30))
    gender = db.Column(db.String(30))


class Favorites(db.Model):
    __tablename__ = 'favorites'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    planet = db.relationship(Planets)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    character = db.relationship(Characters)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user = db.relationship(User)
