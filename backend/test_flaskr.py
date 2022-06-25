import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','Temilorun123_','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            "question": "Who was Nigeria\'s best president?",
            "answer":  "President Umaru Musa Yar\'adua",
            "difficulty": 1,
            "category": 3,
        }
        self.new_quiz = {
            "previous_questions": [12, 22, 1, 18],
            "quiz_category": "Science"
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/api/v1.0/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))


    def test_404_sent__category_return(self):
        res = self.client().get("/api/v1.0/categories") 
        data = json.loads(res.data)  
        self.assertTrue(len(data["categories"]))
        # self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()