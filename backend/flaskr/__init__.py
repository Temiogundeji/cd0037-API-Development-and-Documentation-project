from ast import Not
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from itsdangerous import NoneAlgorithm

from sqlalchemy import null

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end =  start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions =  questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
  # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        ) 
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/api/v1.0/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {cat.id:cat.type for cat in categories}

        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "categories": formatted_categories,
            }
        )

    """
    @TODO:


    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/api/v1.0/questions", methods=["GET"])
    def get_paginated_questions() :
        selections = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {cat.id:cat.type for cat in categories}
        current_questions = paginate_questions(request, selections)
        current_category = list(formatted_categories.values())[0]
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            "questions": current_questions,
            "totalQuestions": len(selections),
            "categories":formatted_categories,
            "currentCategory": current_category
        })      
            
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/api/v1.0/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None: 
                abort(404)
            
            question.delete()

            return jsonify({
                "success": True,
                "deleted" : question_id
            })
        except:
            abort(422)

    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """



    @app.route('/api/v1.0/questions', methods=["POST"])
    def create_question():
        body = request.get_json()
        categories = Category.query.order_by(Category.id).all()
        search_term = body.get("searchTerm", None)
        formatted_categories = {cat.id:cat.type for cat in categories}
        current_category = list(formatted_categories.values())[0]
        if search_term:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search_term)))
            current_questions = paginate_questions(request, selection)
            
            return jsonify({
                "success": True,
                "questions": current_questions,
                "currentCategory": current_category,
                "totalQuestions": len(selection.all())
            })
        else:
            question = body.get("question", None)
            answer = body.get("answer", None)
            difficulty = body.get("difficulty", None)
            category = body.get("category", None)

            if len(question) == 0:
                abort(400)
            if not body:
                abort(400)
            if 'question' in body and type(question) != str:
                abort(400)
            if 'answer' in body and  type(answer) != str:
                abort(400)
            if 'difficulty' in body and type(difficulty) != int:
                abort(400)
            if 'category' in body and type(category) != int:
                abort(400)
            
            
            new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            new_question.insert()
            return jsonify({
                "success": True,
            })

    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/api/v1.0/categories/<int:category_id>/questions', methods=["GET"])
    def fetch_questions_by_category(category_id):
        
        selection = Question.query.filter(Question.category == category_id).all()
        current_category = Category.query.filter(Category.id == category_id)
        formatted_categories = {cat.id:cat.type for cat in current_category}
        current_category = formatted_categories[category_id]
        current_questions =  paginate_questions(request, selection)
        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "totalQuestions": len(selection),
                "currentCategory": current_category
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/api/v1.0/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get("previous_questions")
        quiz_category = body.get("quiz_category")
        current_category_id = quiz_category.get("id")
        category_all = "0"
        questions = None


        if current_category_id == category_all:
            questions = Question.query.all() 
        else:
            questions = Question.query.filter(Question.category == current_category_id).all()

        formatted_questions =  [category_questions for category_questions in questions]
        formatted_questions_ids = set([question.id for question in formatted_questions])
        previous_questions_ids = set(previous_questions)

        if len(formatted_questions_ids) == 0:
            return jsonify({
                "success": True,
                "question": None
            })
        else:
            fresh_question_in_category  = list(formatted_questions_ids - previous_questions_ids)
            next_question_id = random.choice(fresh_question_in_category)
            next_question = Question.query.filter(Question.id == next_question_id).one_or_none()

            return jsonify({
                "question": next_question.format(),
                "success": True
            })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
            }),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
             "error": 422,
             "message": "unprocessable"
            }),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500



    return app

