import os
from flask import Flask, request, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, User

QUESTIONS_PER_PAGE = 10


def questions_pagination(request, selection):
    """
    to paginate questions (10 questions per page)
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # https://flask-cors.readthedocs.io/en/latest/

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

# ----------------------------------------------------------------------------#
# An endpoint to get all available categories .
# ----------------------------------------------------------------------------#

    @app.route("/categories")
    def get_all_categories():
        # query the database to get all categories
        categories_query = Category.query.all()
        if len(categories_query) != 0:
            categories = {}
            # adding all categories to the dict
            for category in categories_query:
                categories[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories
            })

        # if there are categories
        abort(404)

# ----------------------------------------------------------------------------#
# An endpoint to get questions paginated (every 10 questions).
# This endpoint returns a list of questions, number of total questions, current category, categories.
# ----------------------------------------------------------------------------#

    @app.route('/questions')
    def get_all_questions():
        try:
            # get all questions
            selection = Question.query.order_by(Question.id).all()

            # get questions in a page (10 questions per page)
            paginated_questions = questions_pagination(request, selection)

            # if there are questions
            if (len(paginated_questions) != 0):
                # query the database to get all categories
                categories_query = Category.query.all()
                categories_dict = {}
                for category in categories_query:
                    categories_dict[category.id] = category.type

                return jsonify({
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': len(selection),
                    'categories': categories_dict
                })
            abort(404)
        except:
            abort(400)


# ----------------------------------------------------------------------------#
# An endpoint to delete existing question
# ----------------------------------------------------------------------------#

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question is not None:
            try:
                # if the question exists
                if question is not None:
                    # delete it and commit the deletion
                    question.delete()
                    # send back the new paginated questions list to update front end
                    selection = Question.query.order_by(Question.id).all()
                    # paginated_questions = questions_pagination(request, selection)

                return jsonify({
                    'success': True,
                    'question_deleted_id': question_id,
                    'total_questions': len(selection),
                    # 'questions': paginated_questions,
                })
            except:
                abort(422)
        abort(404)

# ----------------------------------------------------------------------------#
# An endpoint to create new questions
# ----------------------------------------------------------------------------#

    @app.route("/questions", methods=['POST'])
    def create_question():

        # load request body and data
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        # ensure all fields are filled
        if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
            abort(422)
        try:
            # Create and insert new question
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty,
                                category=new_category)
            question.insert()

            # get all questions and paginate
            # selection = Question.query.order_by(Question.id).all()
            # current_questions = questions_pagination(request, selection)

            return jsonify({
                'success': True,
                'new_question_id': question.id,
                'new_question': question.question,
                'total_questions': len(Question.query.all()),
                # 'questions': current_questions,
            })
        except:
            abort(422)


# ----------------------------------------------------------------------------#
# An endpoint to get questions based on a search term
# ----------------------------------------------------------------------------#

    @ app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get user input
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        try:
            # If there is a search term query the database for questions with matched term
            if search_term is not None:
                selection = Question.query.filter(Question.question.ilike
                                                  (f'%{search_term}%')).all()
            else:
                # if search term is empty grab all the questions from the database
                selection = Question.query.order_by(Question.id).all()

            # paginate and return results
            paginated_questions = questions_pagination(request, selection)

            return jsonify({
                'success': True,
                'questions':  paginated_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        except:
            abort(404)


# ----------------------------------------------------------------------------#
# An endpoint to get questions based on category.
# ----------------------------------------------------------------------------#

    @ app.route("/categories/<int:category_id>/questions")
    def questions_per_category(category_id):
        # query the database for category with the given id
        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is not None:
            # query the database to get all questions of that category
            questions_per_category = Question.query.filter_by(
                category=str(category_id)).all()

            # if there are questions paginate them
            if questions_per_category is not None:
                paginated_questions = questions_pagination(
                    request, questions_per_category)

                return jsonify({
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': len(questions_per_category),
                    'current_category': category.type
                })
            # if there are no questions in category
            abort(404)
        # if category not found
        abort(404)


# ----------------------------------------------------------------------------#
# An endpoint to get questions to play the quiz.
# This endpoint take category and previous question parameters
# and return a random questions within the given category,
# if provided, and that is not one of the previous questions.
# ----------------------------------------------------------------------------#

    @ app.route('/quizzes', methods=['POST'])
    def quiz_game():

        # grab user inputs
        body = request.get_json()
        category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        # added to pick the score
        correct_answer = body.get('num_correct')
        forceEnd = body.get('forceEnd')

        # CHALLENGE 3
        # query the database to get the last user id
        # used for score calculation and player identification
        user_query = User.query.order_by(User.id.desc()).first()

        # explanation: let's suppose we have a user in the database with ID=1 and username='Player 1'
        # the code below will fetch the database to get the last user id (which is 1 in our case) and
        # increment it in order to generate the new username of player 2
        # if there is no user in the database the id will be 1 else it will be the last user id incremented by 1
        if user_query is not None:
            # add +1 to the id value
            id = int(user_query.id) + 1
        else:
            # if there is no user
            id = 1
        # generate user username
        username = 'Player ' + str(id)
        # print(username)

        try:
            # if user picked 'ALL' categories
            if category['type'] == 'click':
                # filter available questions
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                # filter available questions per category and eliminate used questions
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(
                        Question.id.notin_((previous_questions))).all()

            # select next question from available questions randomly using random.randrange
            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(
                    available_questions) > 0 else None
            # CHALLENGE2 add score to each user
            # score can be tracked using http://127.0.0.1:5000/users
            if new_question is None or forceEnd is True:
                # create a user and add score and save it
                user = User(score=correct_answer, username=username)
                user.insert()
                # print(user.format())
            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)

# ----------------------------------------------------------------------------#
# CHALLENGE 2 get user
# score can be tracked using http://127.0.0.1:5000/users
# ----------------------------------------------------------------------------#
    @ app.route('/users', methods=['GET'])
    def get_users():
        # query the database for users (players)
        selection = User.query.order_by(User.score.desc()).all()

        if len(selection) > 0:
            # players pagination (each 10 players per page)
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            users = [user.format() for user in selection]
            users[start:end]

            return jsonify({
                'success': True,
                'users': users,
                'total_users': len(selection),
            })
        # if there are no players
        abort(404)


# ----------------------------------------------------------------------------#
# CHALLENGE2 add user
# ----------------------------------------------------------------------------#


    @ app.route('/users', methods=['POST'])
    def add_user():
        # get the body from request
        body = request.get_json()

        # get user input
        username = body.get('username', None)
        # make sure inputs are not empty
        if username is not None:
            try:
                # create user and add it to database
                user = User(username=username, score=0)
                user.insert()

                return jsonify({
                    'success': True,
                    'message': 'User created successfully',
                    'new_user_id': user.id,
                    'username': user.username,
                })
            except:
                abort(422)
        abort(422)

# ----------------------------------------------------------------------------#
# CHALLENGE 3: add category
# ----------------------------------------------------------------------------#
    @ app.route('/categories', methods=['POST'])
    def add_category():
        # get the body from request
        body = request.get_json()

        # get user input
        type = body.get('type', None)
        if type is not None:
            try:
                # create category and add it to database
                category = Category(type=type.capitalize())
                category.insert()

                return jsonify({
                    'success': True,
                    'message': 'Category created successfully',
                    'new_category_id': category.id,
                    'new_category_type': category.type,
                })
            except:
                abort(422)
        abort(422)


# ----------------------------------------------------------------------------#
# Error handlers
# ----------------------------------------------------------------------------#

    @ app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @ app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @ app.errorhandler(422)
    def unprocessable_resource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable resource"
        }), 422

    @ app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @ app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method"
        }), 405

    return app
