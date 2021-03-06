"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
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

@app.route('/get_fav', methods=['GET'])
def get_fav():

    # get all the people
    query = Favorites.query.all()

    # map the results and your list of people  inside of the all_people variable
    all_favs = list(map(lambda x: x.serialize(), query))

    return jsonify(all_favs), 200

@app.route('/add_fav', methods=['POST'])
def add_fav():

    request_body = request.get_json()
    fav = Favorites(name=request_body["name"])
    db.session.add(fav)
    db.session.commit()

    return jsonify("Favorito agregado de forma correcta."), 200

@app.route('/upd_fav/<int:fid>', methods=['PUT'])
def upd_fav(fid):

    fav = Favorites.query.get(fid)
    if fav is None:
        raise APIException('Favorite not found', status_code=404)

    request_body = request.get_json()

    if "name" in request_body:
        fav.name = request_body["name"]

    db.session.commit()
    return jsonify("Favorito modificado de forma correcta."), 200

@app.route('/del_fav/<int:fid>', methods=['DELETE'])
def del_fav(fid):

    fav = Favorites.query.get(fid)

    if fav is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(fav)
    db.session.commit()

    return jsonify("Favorito eliminado de forma correcta."), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
