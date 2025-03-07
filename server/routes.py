from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models import db, User, Recipe


class Signup(Resource):
    def post(self):
        """Handles user registration."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        image_url = data.get("image_url")
        bio = data.get("bio")

        # Input validation
        errors = {}

        if not username:
            errors["username"] = "Username is required."
        elif User.query.filter_by(username=username).first():
            errors["username"] = "Username already exists."

        if not password:
            errors["password"] = "Password is required."

        if errors:
            return {"errors": errors}, 422

        # Create new user
        user = User(username=username, image_url=image_url, bio=bio)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id  # Store session

        return {
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio,
        }, 201


class CheckSession(Resource):
    def get(self):
        """Checks if a user is logged in and returns their details."""
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)  # ✅ FIXED for SQLAlchemy 2.0
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio,
                }, 200
        return {"error": "Unauthorized"}, 401


class Login(Resource):
    def post(self):
        """Handles user login."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):  # ✅ FIXED: using check_password()
            session["user_id"] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio,
            }, 200

        return {"error": "Invalid credentials"}, 401


class Logout(Resource):
    def delete(self):
        """Logs the user out by clearing the session."""
        if "user_id" not in session or session["user_id"] is None:
            return {"error":"Unauthorized"}, 401
        session.pop("user_id")
        return{}, 204


class RecipeIndex(Resource):
    def get(self):
        """Fetches all recipes for logged-in users."""
        if "user_id" not in session or session["user_id"] is None:
            return {"error": "Unauthorized"}, 401  # ✅ FIXED: Ensures login required

        recipes = Recipe.query.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user": {"id": r.user.id, "username": r.user.username},
            }
            for r in recipes
        ], 200

    def post(self):
        """Allows a logged-in user to create a recipe."""
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()
        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        # Input validation
        errors = {}

        if not title:
            errors["title"] = "Title is required."
        if not instructions or len(instructions) < 50:
            errors["instructions"] = "Instructions must be at least 50 characters long."
        if not minutes_to_complete or not isinstance(minutes_to_complete, int):
            errors["minutes_to_complete"] = "Minutes to complete must be a valid number."

        if errors:
            return {"errors": errors}, 422  # ✅ FIXED: Proper error responses

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=session["user_id"],
        )

        db.session.add(recipe)
        db.session.commit()

        return {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {"id": recipe.user.id, "username": recipe.user.username},
        }, 201
