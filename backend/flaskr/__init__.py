import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
BASE_URL = '/api/v0.1.0'
question_count = 0
error = 0


def set_error_code(code):
    global error
    error = code


def get_error_code():
    global error
    return error


def get_paginated_questions(page=1, q_per_page=QUESTIONS_PER_PAGE, search_term=None, category_id=None):
    global question_count

    query = Question.query

    if search_term is not None:
        query = query.filter(Question.question.ilike(f'%{search_term}%'))
        if query.count() == 0:
            return None

    if category_id is not None and not category_id == 0:
        query = query.filter(Question.category == category_id)
        if query.count() == 0:
            return None

    question_count = query.count()

    query = query.order_by(Question.id).offset(
        (page-1)*q_per_page).limit(q_per_page).all()

    return query


def get_categories(for_quiz=False):
    categories = Category.query.order_by(Category.id).all()

    return_categories = {}

    for category in categories:
        if for_quiz:
            if get_paginated_questions(category_id=category.format()['id']) is not None:
                return_categories[str(category.format()['id'])] = category.format()[
                    'type']
        else:
            return_categories[str(category.format()['id'])] = category.format()[
                'type']

    return return_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"{BASE_URL}/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
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
    @app.route(f"{BASE_URL}/categories")
    def retrieve_categories():
        try:
            categories = get_categories(for_quiz="quiz" in request.args)

            return jsonify({
                "success": True,
                "categories": categories
            })
        except:
            abort(500)

    @app.route(f'{BASE_URL}/categories', methods=['POST'])
    def create_category():
        try:
            try:
                incoming_category = request.get_json()['category']
                if incoming_category == '':
                    raise
            except:
                set_error_code(400)
                raise

            category = Category.query.filter(
                Category.type == incoming_category).first()

            if category is None:
                new_category = Category(type=request.get_json()['category'])
                new_category.insert()

                return jsonify({
                    "success": True,
                })
            else:
                set_error_code(403)
                raise
        except:
            abort(get_error_code())

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
    @app.route(f'{BASE_URL}/questions')
    def retrieve_questions():
        try:
            page = request.args.get('page', 1, type=int)
            questions = get_paginated_questions(
                page=page)

            if not questions:
                raise

            return_questions = []
            for question in questions:
                return_questions.append(question.format())

            return jsonify({
                "success": True,
                "questions": return_questions,
                "total_questions": question_count,
                "categories": get_categories(),
                "current_category": "All"
            })
        except:
            abort(404)
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route(f'{BASE_URL}/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()

            return jsonify({
                "success": True,
                "deleted_id": question.format()['id'],
            })
        except:
            abort(422)

    @app.route(f'{BASE_URL}/questions', methods=['POST'])
    def create_or_search_questions():
        if request.get_json() and "searchTerm" in request.get_json():
            """
            @TODO:
            Create a POST endpoint to get questions based on a search term.
            It should return any questions for whom the search term
            is a substring of the question.

            TEST: Search by any phrase. The questions list will update to include
            only question that include that string within their question.
            Try using the word "title" to start.
            """
            if request.get_json()["searchTerm"] == '':
                abort(422)
            try:
                search_term = request.get_json()["searchTerm"]
                questions = get_paginated_questions(
                    search_term=search_term, q_per_page=1000)

                if not questions:
                    raise

                return_questions = []
                for question in questions:
                    return_questions.append(question.format())

                return jsonify({
                    "success": True,
                    "questions": return_questions,
                    "total_questions": question_count,
                    "current_category": "All"
                })
            except:
                abort(404)
        else:
            """
            @TODO:
            Create an endpoint to POST a new question,
            which will require the question and answer text,
            category, and difficulty score.

            TEST: When you submit a question on the "Add" tab,
            the form will clear and the question will appear at the end of the last page
            of the questions list in the "List" tab.
            """
            try:
                data = request.get_json()

                question = data['question']
                answer = data['answer']
                category = int(data['category'])
                difficulty = int(data['difficulty'])

                if not (question and answer and category and difficulty):
                    raise

                new_question = Question(
                    question=question, answer=answer, category=category, difficulty=difficulty)
                new_question.insert()

                return jsonify({
                    "success": True,
                })
            except:
                abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route(f'{BASE_URL}/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            questions = get_paginated_questions(category_id=category_id)

            if not questions:
                raise

            return_questions = []
            for question in questions:
                return_questions.append(question.format())

            return jsonify({
                "success": True,
                "questions": return_questions,
                "total_questions": question_count,
                "current_category": Category.query.get(category_id).format()['type']
            })
        except:
            abort(404)

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
    @app.route(f'{BASE_URL}/quizzes', methods=['POST'])
    def load_quiz():
        try:
            category_id = request.get_json()['quiz_category']['id']
            previous_questions = request.get_json()['previous_questions']

            questions = get_paginated_questions(category_id=category_id)

            queue = []
            for question in [question.format() for question in questions]:
                if not question['id'] in previous_questions:
                    queue.append(question)

            return_question = {}
            upper_range = len(queue)
            if upper_range > 0:
                return_question = queue[math.floor(
                    random.randrange(0, upper_range))]
            return jsonify({
                "success": True,
                "question": return_question,
            })
        except:
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 422,
                    "message": "unprocessable",
                }
            ),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "bad request",
                }
            ),
            400,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 405,
                    "message": "method not allowed"
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                }
            ),
            500,
        )

    @app.errorhandler(403)
    def forbidden(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 403,
                    "message": "forbidden"
                }
            ),
            403,
        )

    return app
