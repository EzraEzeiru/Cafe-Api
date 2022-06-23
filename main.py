from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
secret_key = "Sports14"


##  Café TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    all_cafes = Cafe.query.all()
    number_of_cafes = len(all_cafes)
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafe():
    all_cafes = Cafe.query.all()
    return jsonify(all_cafe=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search_for_cafe():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location)
    if cafes:
        return jsonify(all_cafe=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found: Sorry we do not have a cafe at that location"})


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = Cafe.query.get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"Success": "Successfully updated the price"}), 200

    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 400


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == secret_key:
        cafe = Cafe.query.get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "The record has been deleted successfully"}), 200

        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 400
    else:
        return jsonify({"Forbidden": "Sorry that's not allowed. Make sure you have the correct API KEY"}), 403


if __name__ == '__main__':
    app.run(debug=True)
