from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json


'''Blueprint for our application'''

views = Blueprint('views', __name__)


@views.route('/', methods=["GET", "POST"]) #endpoint for home page
@login_required
def home():
    '''Function to be called when home page is hit'''
    if request.method == 'POST':
        note = request.form.get('note')
        if len(note) < 1:
            flash("Note is empty.", category="error")
        else:
            new_note = Note(content=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash("Noted!", category="success")
    return render_template("home.html", user=current_user) #reference current user and check if it is authenticated to get their notes


@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = json.loads(request.data)
    note_id = data['noteId']
    print("deleting note", note_id)
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
