#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        """Handles user registration."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        image_url = data.get("image_url")
        bio = data.get("bio")

        if not username or not password:
            return {"error": "Username and password are required."}, 422

        try:
            user = User(username=username, image_url=image_url, bio=bio)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio,
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists."}, 422


class CheckSession(Resource):
    def get(self):
        """Checks if a user is logged in."""
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)
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
        if user and user.check_password(password):
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
        """Logs the user out."""
        if "user_id" not in session or session["user_id"] is None:
            return {"error": "Unauthorized"}, 401  # ✅ Fixed error response

        session.pop("user_id")
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        """Fetches all recipes for logged-in users."""
        if "user_id" not in session or session["user_id"] is None:
            return {"error": "Unauthorized"}, 401

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

        if not title:
            return {"error": "Title is required."}, 422
        if not instructions or len(instructions) < 50:
            return {"error": "Instructions must be at least 50 characters long."}, 422
        if not isinstance(minutes_to_complete, int) or minutes_to_complete <= 0:
            return {"error": "Minutes to complete must be a positive integer."}, 422

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
        }, 201  # ✅ Fix: Ensure correct response


api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
