from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", back_populates="user", lazy=True, cascade="all, delete")

    serialize_rules = ("-recipes.user",)

    def set_password(self, password):
        """Hashes the password before storing it."""
        self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Checks if a given password matches the stored hashed password."""
        return bcrypt.check_password_hash(self._password_hash, password)

    def authenticate(self, password):  # ✅ Fix: Added `authenticate()`
        """Authenticate user by checking password."""
        return self.check_password(password)
    

class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # ✅ Ensuring `user_id` is NOT NULL

    user = db.relationship("User", back_populates="recipes")

    @validates("title")
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title cannot be empty.")
        return title

    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions

    @validates("user_id")
    def validate_user_id(self, key, user_id):
        if not user_id:
            raise ValueError("Every recipe must be linked to a valid user.")
        return user_id  # ✅ Ensuring every recipe has a valid user_id


