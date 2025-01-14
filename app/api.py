from flask import Flask, jsonify, request
from app.database import Session, UserModel, TransactionModel

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Invalid input"}), 400

    session = Session()
    if session.query(UserModel).filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400

    user = UserModel(username=data["username"], email=data["email"], password_hash=data["password"])
    session.add(user)
    session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not all(k in data for k in ("username", "password")):
        return jsonify({"error": "Invalid input"}), 400

    session = Session()
    user = session.query(UserModel).filter_by(username=data["username"]).first()
    if not user or user.password_hash != data["password"]:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful"}), 200

@app.route("/balance", methods=["GET"])
def balance():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400

    session = Session()
    user = session.query(UserModel).filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"balance": user.balance}), 200

@app.route("/add_balance", methods=["POST"])
def add_balance():
    data = request.json
    if not data or not all(k in data for k in ("username", "amount")):
        return jsonify({"error": "Invalid input"}), 400

    session = Session()
    user = session.query(UserModel).filter_by(username=data["username"]).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.balance += data["amount"]
    session.commit()
    return jsonify({"message": "Balance updated successfully", "new_balance": user.balance}), 200

if __name__ == "__main__":
    app.run(debug=True)