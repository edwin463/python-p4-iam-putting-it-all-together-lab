from faker import Faker
import flask
import pytest
from random import randint, choice as rc

from app import app
from models import db, User, Recipe

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

class TestSignup:
    '''Signup resource in app.py'''

    def test_creates_users_at_signup(self):
        '''creates user records with usernames and passwords at /signup.'''
        
        with app.app_context():
            User.query.delete()
            db.session.commit()
        
        with app.test_client() as client:
            response = client.post('/signup', json={
                'username': 'ashketchum',
                'password': 'pikachu',
                'bio': 'Trainer of the best Pokémon.',
                'image_url': 'https://pokemon.com/ash.jpg',
            })

            assert(response.status_code == 201)

            new_user = User.query.filter(User.username == 'ashketchum').first()

            assert(new_user)
            assert(new_user.check_password('pikachu'))  # ✅ FIXED
            assert(new_user.image_url == 'https://pokemon.com/ash.jpg')
            assert(new_user.bio == 'Trainer of the best Pokémon.')

class TestRecipeIndex:
    '''RecipeIndex resource in app.py'''

    def test_lists_recipes_with_200(self):
        '''returns a list of recipes associated with the logged in user and a 200 status code.'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            fake = Faker()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(nb_sentences=3),
                image_url=fake.url(),
            )

            user.set_password('secret')  # ✅ FIXED
            db.session.add(user)
            db.session.commit()

            recipes = []
            for i in range(15):
                instructions = fake.paragraph(nb_sentences=8)
                
                recipe = Recipe(
                    title=fake.sentence(),
                    instructions=instructions,
                    minutes_to_complete=randint(15, 90),
                    user_id=user.id  # ✅ FIXED
                )

                recipes.append(recipe)

            db.session.add_all(recipes)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={
                'username': 'Slagathor',
                'password': 'secret',
            })
        
            response = client.get('/recipes')
            response_json = response.get_json()

            assert response.status_code == 200
            for i in range(15):
                assert response_json[i]['title']
                assert response_json[i]['instructions']
                assert response_json[i]['minutes_to_complete']

    def test_get_route_returns_401_when_not_logged_in(self):
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = None

            response = client.get('/recipes')
            
            assert response.status_code == 401

    def test_creates_recipes_with_201(self):
        '''creates recipes successfully'''

        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            fake = Faker()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(nb_sentences=3),
                image_url=fake.url(),
            )
            user.set_password('secret')  # ✅ FIXED
            
            db.session.add(user)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={
                'username': 'Slagathor',
                'password': 'secret',
            })
            
            response = client.post('/recipes', json={
                'title': fake.sentence(),
                'instructions': fake.paragraph(nb_sentences=8),
                'minutes_to_complete': randint(15,90)
            })

            assert response.status_code == 201

    def test_returns_422_for_invalid_recipes(self):
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            fake = Faker()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(nb_sentences=3),
                image_url=fake.url(),
            )
            user.set_password('secret')  # ✅ FIXED
            
            db.session.add(user)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={
                'username': 'Slagathor',
                'password': 'secret',
            })
            
            response = client.post('/recipes', json={
                'title': fake.sentence(),
                'instructions': 'Short text',
                'minutes_to_complete': randint(15, 90)
            })

            assert response.status_code == 422  # ✅ FIXED
