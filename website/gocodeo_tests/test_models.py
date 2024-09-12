import pytest
from unittest.mock import patch, MagicMock
from website.models import Note, User

@pytest.fixture
def setup_database():
    with patch('website.models.db') as mock_db, \
         patch('website.models.func') as mock_func:
        
        # Mocking the database session and query methods
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_db.Model = MagicMock()
        mock_db.Column = MagicMock()
        mock_db.Integer = MagicMock()
        mock_db.String = MagicMock()
        mock_db.DateTime = MagicMock()
        mock_db.ForeignKey = MagicMock()
        mock_db.relationship = MagicMock()

        # Mocking SQLAlchemy func.now() method
        mock_func.now.return_value = MagicMock()

        # Ensure the Note and User classes are mocked properly
        mock_note = MagicMock()
        mock_user = MagicMock()
        mock_db.Model.return_value = mock_note
        mock_db.Model.return_value = mock_user

        yield mock_db, mock_func, mock_note, mock_user

# happy_path - test_create_note_with_valid_data - Test that a Note can be created with valid content, date, and user_id
def test_create_note_with_valid_data(setup_database):
    db, func, mock_note, mock_user = setup_database
    note_instance = Note(content='This is a test note', user_id=1)
    db.session.add.assert_called_with(note_instance)
    db.session.commit.assert_called_once()
    assert note_instance.content == 'This is a test note'
    assert note_instance.user_id == 1
    assert note_instance.id is not None

# happy_path - test_create_user_with_unique_email - Test that a User can be created with a unique email and valid password
def test_create_user_with_unique_email(setup_database):
    db, func, mock_note, mock_user = setup_database
    user_instance = User(email='test@example.com', password='securepassword', first_name='John')
    db.session.add.assert_called_with(user_instance)
    db.session.commit.assert_called_once()
    assert user_instance.email == 'test@example.com'
    assert user_instance.first_name == 'John'
    assert user_instance.id is not None

# happy_path - test_note_association_with_user - Test that a Note is associated with the correct User
def test_note_association_with_user(setup_database):
    db, func, mock_note, mock_user = setup_database
    note_instance = Note(content="User's note", user_id=2)
    db.session.add.assert_called_with(note_instance)
    db.session.commit.assert_called_once()
    assert note_instance.user_id == 2

# happy_path - test_user_with_multiple_notes - Test that a User can have multiple Notes
def test_user_with_multiple_notes(setup_database):
    db, func, mock_note, mock_user = setup_database
    user_instance = User(email='user2@example.com', password='anotherpassword', first_name='Jane')
    note1 = Note(content='First note')
    note2 = Note(content='Second note')
    user_instance.notes.extend([note1, note2])
    db.session.add.assert_called_with(user_instance)
    db.session.commit.assert_called_once()
    assert len(user_instance.notes) == 2

# happy_path - test_note_default_date - Test that Notes have a default date when created
def test_note_default_date(setup_database):
    db, func, mock_note, mock_user = setup_database
    note_instance = Note(content='Note with default date', user_id=3)
    db.session.add.assert_called_with(note_instance)
    db.session.commit.assert_called_once()
    assert note_instance.date is not None

# edge_case - test_create_note_with_long_content - Test that creating a Note with an excessively long content raises an error
def test_create_note_with_long_content(setup_database):
    db, func, mock_note, mock_user = setup_database
    long_content = 'x' * 1001
    with pytest.raises(Exception) as excinfo:
        note_instance = Note(content=long_content, user_id=4)
        db.session.add(note_instance)
        db.session.commit()
    assert 'StringDataRightTruncation' in str(excinfo.value)

# edge_case - test_create_user_with_duplicate_email - Test that creating a User with a non-unique email raises an error
def test_create_user_with_duplicate_email(setup_database):
    db, func, mock_note, mock_user = setup_database
    user_instance1 = User(email='duplicate@example.com', password='password1', first_name='Alice')
    db.session.add(user_instance1)
    db.session.commit()
    user_instance2 = User(email='duplicate@example.com', password='password2', first_name='Bob')
    with pytest.raises(Exception) as excinfo:
        db.session.add(user_instance2)
        db.session.commit()
    assert 'IntegrityError' in str(excinfo.value)

# edge_case - test_create_note_without_user_id - Test that creating a Note without a user_id raises an error
def test_create_note_without_user_id(setup_database):
    db, func, mock_note, mock_user = setup_database
    with pytest.raises(Exception) as excinfo:
        note_instance = Note(content='Note without user')
        db.session.add(note_instance)
        db.session.commit()
    assert 'IntegrityError' in str(excinfo.value)

# edge_case - test_create_user_without_email - Test that creating a User without an email raises an error
def test_create_user_without_email(setup_database):
    db, func, mock_note, mock_user = setup_database
    with pytest.raises(Exception) as excinfo:
        user_instance = User(password='noemailpassword', first_name='Bob')
        db.session.add(user_instance)
        db.session.commit()
    assert 'IntegrityError' in str(excinfo.value)

# edge_case - test_create_note_with_negative_user_id - Test that a Note cannot be created with a negative user_id
def test_create_note_with_negative_user_id(setup_database):
    db, func, mock_note, mock_user = setup_database
    with pytest.raises(Exception) as excinfo:
        note_instance = Note(content='Invalid user_id note', user_id=-1)
        db.session.add(note_instance)
        db.session.commit()
    assert 'IntegrityError' in str(excinfo.value)

