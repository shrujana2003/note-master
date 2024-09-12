import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User
from website import db
from flask_login import login_user, logout_user, current_user

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        yield app.test_client()

@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.email = 'test@example.com'
    user.password = generate_password_hash('correct_password')
    return user

@pytest.fixture
def mock_new_user():
    user = MagicMock(spec=User)
    user.email = 'newuser@example.com'
    user.first_name = 'John'
    user.password = generate_password_hash('validpassword')
    return user

@pytest.fixture
def mock_db_session():
    with patch('website.db.session', autospec=True) as mock_session:
        yield mock_session

@pytest.fixture
def mock_login_user():
    with patch('flask_login.login_user', autospec=True) as mock_login:
        yield mock_login

@pytest.fixture
def mock_logout_user():
    with patch('flask_login.logout_user', autospec=True) as mock_logout:
        yield mock_logout

@pytest.fixture
def mock_check_password_hash():
    with patch('werkzeug.security.check_password_hash', autospec=True) as mock_check:
        yield mock_check

@pytest.fixture
def mock_generate_password_hash():
    with patch('werkzeug.security.generate_password_hash', autospec=True) as mock_generate:
        yield mock_generate

@pytest.fixture
def mock_user_query():
    with patch('website.models.User.query', autospec=True) as mock_query:
        yield mock_query

# happy_path - test_login_success - Test that login is successful with correct email and password
def test_login_success(client, mock_user_query, mock_user, mock_check_password_hash, mock_login_user):
    mock_user_query.filter_by.return_value.first.return_value = mock_user
    mock_check_password_hash.return_value = True

    response = client.post('/login', data={'email': 'test@example.com', 'password': 'correct_password'})

    assert b'Logged In successfully. Welcome Back!' in response.data
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/home')

# happy_path - test_signup_success - Test that signup is successful with valid input data
def test_signup_success(client, mock_user_query, mock_new_user, mock_generate_password_hash, mock_db_session, mock_login_user):
    mock_user_query.filter_by.return_value.first.return_value = None
    mock_generate_password_hash.return_value = 'hashed_password'

    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'validpassword',
        'password2': 'validpassword'
    })

    assert b'Successfully Signed up. Welcome!' in response.data
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/home')

# happy_path - test_logout_redirect - Test that logout redirects to login page
def test_logout_redirect(client, mock_logout_user):
    response = client.get('/logout')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/auth/login')

# edge_case - test_login_incorrect_password - Test that login fails with incorrect password
def test_login_incorrect_password(client, mock_user_query, mock_user, mock_check_password_hash):
    mock_user_query.filter_by.return_value.first.return_value = mock_user
    mock_check_password_hash.return_value = False

    response = client.post('/login', data={'email': 'test@example.com', 'password': 'wrong_password'})

    assert b'Incorrect password' in response.data
    assert response.status_code == 200

# edge_case - test_signup_short_email - Test that signup fails if email is too short
def test_signup_short_email(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None

    response = client.post('/signup', data={
        'email': 'a@b',
        'firstName': 'John',
        'password1': 'validpassword',
        'password2': 'validpassword'
    })

    assert b'Email must be more than 4 characters.' in response.data
    assert response.status_code == 200

# edge_case - test_signup_password_mismatch - Test that signup fails if passwords do not match
def test_signup_password_mismatch(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None

    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'password1',
        'password2': 'password2'
    })

    assert b'Passwords do not match.' in response.data
    assert response.status_code == 200

# edge_case - test_signup_short_password - Test that signup fails if password is too short
def test_signup_short_password(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None

    response = client.post('/signup', data={
        'email': 'newuser@example.com',
        'firstName': 'John',
        'password1': 'short',
        'password2': 'short'
    })

    assert b'Passwords must be at least 8 characters.' in response.data
    assert response.status_code == 200

# edge_case - test_login_user_not_exist - Test that login fails if user does not exist
def test_login_user_not_exist(client, mock_user_query):
    mock_user_query.filter_by.return_value.first.return_value = None

    response = client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'password'})

    assert b'No such user. Please sign up' in response.data
    assert response.status_code == 200

