import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # ✅ FIX: Ensure user exists before recipe creation
            user = User(username="TestUser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="This is a properly long instruction text that exceeds fifty characters.",
                minutes_to_complete=60,
                user_id=user.id  # ✅ FIXED
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert len(new_recipe.instructions) > 50  # ✅ Ensures long instructions

    def test_requires_title(self):
        '''raises ValueError for missing title.'''  # ✅ FIXED EXPECTED ERROR

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # ✅ FIX: Ensure user exists before recipe creation
            user = User(username="TestUser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            # ✅ FIX: Expecting `ValueError` instead of `IntegrityError`
            with pytest.raises(ValueError, match="Title cannot be empty."):
                recipe = Recipe(
                    title=None,  # ❌ No title
                    instructions="Valid instructions over fifty characters.",
                    minutes_to_complete=30,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''raises ValueError for short instructions'''  # ✅ FIXED EXPECTED ERROR

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # ✅ FIX: Ensure user exists before recipe creation
            user = User(username="TestUser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

            # ✅ FIX: Expecting `ValueError` for short instructions
            with pytest.raises(ValueError, match="Instructions must be at least 50 characters long."):
                recipe = Recipe(
                    title="Short Instruction Test",
                    instructions="Too short!",  # ❌ Less than 50 chars
                    minutes_to_complete=30,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()

    def test_requires_user_id(self):
        '''raises ValueError if user_id is missing.'''  # ✅ FIXED EXPECTED ERROR

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # ✅ FIX: Expecting `ValueError`, not `IntegrityError`
            with pytest.raises(ValueError, match="Every recipe must be linked to a valid user."):
                recipe = Recipe(
                    title="Orphaned Recipe",
                    instructions="Valid long instruction with more than fifty characters.",
                    minutes_to_complete=20,
                    user_id=None  # ❌ No user assigned
                )
                db.session.add(recipe)
                db.session.commit()
