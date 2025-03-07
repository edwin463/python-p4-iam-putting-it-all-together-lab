#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Recipe, User

fake = Faker()

with app.app_context():

    print("Deleting all records...")
    db.session.query(Recipe).delete()
    db.session.query(User).delete()
    db.session.commit()

    print("Creating users...")

    users = []
    usernames = set()

    for _ in range(20):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        user = User(
            username=username,
            bio=fake.paragraph(nb_sentences=3),
            image_url=fake.url(),
        )

        user.set_password("defaultpassword")  # ✅ Ensuring password is set
        users.append(user)

    db.session.add_all(users)
    db.session.commit()  # ✅ Committing users to ensure they exist before adding recipes

    print("Creating recipes...")
    recipes = []
    for _ in range(100):
        instructions = fake.paragraph(nb_sentences=5)

        user = rc(users)  # ✅ Assign recipe to a **valid existing user**
        recipe = Recipe(
            title=fake.sentence(nb_words=5),
            instructions=instructions,
            minutes_to_complete=randint(15, 90),
            user_id=user.id,  # ✅ Ensuring this is always set
        )

        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()  # ✅ Committing all changes to the database

    print("Seeding complete!")
