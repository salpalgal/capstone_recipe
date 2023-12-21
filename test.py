import os
from unittest import TestCase
from flask import g, session
from models import db, connect_db, Recipe, User, Favorite

os.environ['DATABASE_URL'] = "postgresql:///recipe-test"

from app import app, CURR_USER_KEY


app.config['WTF_CSRF_ENABLED'] = False


class RecipeViewTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

        
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1001
        self.testuser.id = self.testuser_id

        db.session.commit()
       
        
    def test_search(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post("/search", data = {"ingredients": "chicken", "number":1}, follow_redirects= True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1> searched recipes list</h1>", html)
            self.assertIn("Number of Missed Ingredients", html)
    def test_user_show(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            res = client.get(f"/user/{self.testuser.id}")

            self.assertEqual(res.status_code, 200)

    def test_add_fav(self):
        r1 = Recipe(id = 3333, user_id = self.testuser.id, api_recipe_id = 12345)
        db.session.add(r1)
        db.session.commit()
    
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY]= self.testuser.id
                sess['res'] = []
            resp = client.post("/recipe/3333/fav", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            favs = Favorite.query.filter(Favorite.recipe_id == 3333).all()

            self.assertEqual(len(favs), 1)

    def test_remove_fav(self):
        r1 = Recipe(id = 3333, user_id = self.testuser.id, api_recipe_id = 12345)
        db.session.add(r1)
        db.session.commit()
        fav = Favorite(user_id = self.testuser.id, recipe_id = 3333)
        db.session.add(fav)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess['res'] = []
            resp = client.post("recipe/3333/unfav", follow_redirects = True)

            self.assertEqual(resp.status_code, 200)

            f = Favorite.query.filter(Favorite.recipe_id == 3333).all()

            self.assertEqual(len(f), 0)

    def test_login(self):
        with self.client as client:
            res = client.post("/login", data= {"username" :"testuser", "password":"testuser"}, follow_redirects= True)
            html = res.get_data(as_text = True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h3>Welcome testuser!</h3>", html)

    def test_logout(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY]= self.testuser.id
            res = client.get("/logout", follow_redirects = True)
            html = res.get_data(as_text = True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn("root page", html)
