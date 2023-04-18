"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import secrets
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
active_user_id=0

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['POST'])
def create_user():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = User(email=request.json['email'], password=request.json['password'], is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/token', methods=['POST'])
def get_token():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        token = secrets.token_hex(16)
        user.token = token  # Asignar el token al usuario
        db.session.commit()  # Guardar los cambios en la base de datos
        return jsonify({'token': token, 'user': user.serialize()})
    else:
        return jsonify({'message': 'Credenciales inválidas'})

@app.route('/user/me', methods=['GET'])
def get_user_profile():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]  # Obtener el token del encabezado de autenticación
    else:
        auth_token = ''
    if auth_token:
        user = User.query.filter_by(token=auth_token).first()  # Buscar el usuario correspondiente al token
        if user:
            return jsonify({'user': user.serialize()})
        else:
            return jsonify({'message': 'Token inválido'}), 401
    else:
        return jsonify({'message': 'Falta el token de autenticación'}), 401


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    else:
        return jsonify(user.serialize()), 200

@app.route('/planets', methods=['POST'])
def add_planet():
    if not request.json:
        abort(400)
    new_planet = Planets(name=request.json['name'], diameter=request.json['diameter'], rotation_period=request.json['rotation_period'], orbital_period=request.json['orbital_period'], gravity=request.json['gravity'], population=request.json['population'], climate=request.json['climate'], terrain=request.json['terrain'], surface_water=request.json['surface_water'])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    return jsonify([planets.serialize() for planets in planets]), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planets = Planets.query.filter_by(id=planets_id).first()
    if planets is None:
        return jsonify({'message': 'Planeta no encontrado'}), 404
    else:
        return jsonify(planets.serialize()), 200

@app.route('/people', methods=['POST'])
def add_character():
    data = request.get_json()
    if not request.json:
        abort(400)
    new_character = Characters(name=data['name'], height=data['height'], mass=data['mass'],
                                   hair_color=data['hair_color'], skin_color=data['skin_color'],
                                   eye_color=data['eye_color'], birth_year=data['birth_year'],
                                   gender=data['gender'])
    db.session.add(new_character)
    db.session.commit()
    response = jsonify({"message": "Personaje añadido correctamente."})
    return response, 201

@app.route('/people', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()
    results = []
    for character in characters:
        character_data = {
            'id': character.id,
            'name': character.name,
            'height': character.height,
            'mass': character.mass,
            'hair_color': character.hair_color,
            'skin_color': character.skin_color,
            'eye_color': character.eye_color,
            'birth_year': character.birth_year,
            'gender': character.gender
        }
        results.append(character_data)
    return jsonify(results)

@app.route('/people/<int:character_id>', methods=['GET'])
def get_character_by_id(character_id):
    character = Characters.query.filter_by(id=character_id).first()
    if character:
        character_data = {
            'id': character.id,
            'name': character.name,
            'height': character.height,
            'mass': character.mass,
            'hair_color': character.hair_color,
            'skin_color': character.skin_color,
            'eye_color': character.eye_color,
            'birth_year': character.birth_year,
            'gender': character.gender
        }
        return jsonify(character_data)
    else:
        return jsonify({'message': 'Personaje no encontrado'})

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]  # Obtener el token del encabezado de autenticación
    else:
        auth_token = ''
    if auth_token:
        user = User.query.filter_by(token=auth_token).first()  # Buscar el usuario correspondiente al token
        if user:
            planet = Planets.query.get(planet_id)
            if planet:
                favorite = Favorites(planet_id=planet_id, user_id=user.id)
                db.session.add(favorite)
                db.session.commit()
                return jsonify({'message': 'Planeta agregado a favoritos'})
            else:
                return jsonify({'message': 'Planeta no encontrado'}), 404
        else:
            return jsonify({'message': 'Token inválido'}), 401
    else:
        return jsonify({'message': 'Falta el token de autenticación'}), 401

@app.route('/favorite/people/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]  # Obtener el token del encabezado de autenticación
    else:
        auth_token = ''
    if auth_token:
        user = User.query.filter_by(token=auth_token).first()  # Buscar el usuario correspondiente al token
        if user:
            character = Characters.query.get(character_id)
            if character:
                favorite = Favorites(character_id=character_id, user_id=user.id)
                db.session.add(favorite)
                db.session.commit()
                return jsonify({'message': 'Personaje agregado a favoritos'})
            else:
                return jsonify({'message': 'Personaje no encontrado'}), 404
        else:
            return jsonify({'message': 'Token inválido'}), 401
    else:
        return jsonify({'message': 'Falta el token de autenticación'}), 401

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]  # Obtener el token del encabezado de autenticación
    else:
        auth_token = ''
    if auth_token:
        user = User.query.filter_by(token=auth_token).first()  # Buscar el usuario correspondiente al token
        if user:
            favorites = Favorites.query.filter_by(user_id=user.id).all()  # Buscar todos los favoritos del usuario
            response = []
            for favorite in favorites:
                if favorite.planet:
                    response.append({
                        'id': favorite.id,
                        'type': 'planet',
                        'name': favorite.planet.name,
                    })
                elif favorite.character:
                    response.append({
                        'id': favorite.id,
                        'type': 'character',
                        'name': favorite.character.name,
                    })
            return jsonify(response)
        else:
            return jsonify({'message': 'Token inválido'}), 401
    else:
        return jsonify({'message': 'Falta el token de autenticación'}), 401


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
