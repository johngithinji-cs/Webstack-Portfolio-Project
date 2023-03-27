#!/usr/bin/env python3
"""Application routes"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .db import db
from .models.user import User
import os
from os.path import join, dirname, realpath
from flask import current_app
import pandas as pd
import mysql.connector


auth = Blueprint('auth', __name__)

mydb = mysql.connector.connect(
    host="localhost",
    user="analyst",
    password="project",
    database="user_data"
)

uploads_dir = os.path.join(auth.root_path, 'fileUploads')
os.makedirs(uploads_dir, exist_ok=True)


@auth.route('/login')
def login():
  """Route to login page"""
  return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
  """Route for actually logging in"""
  email = request.form.get('email')
  password = request.form.get('password')
  remember = False
  if request.form.get('remember'):
    remember = True

  user = User.query.filter_by(email=email).first()
  if not user or not check_password_hash(user.password, password):
    flash('Please check your login details and try again.')
    return redirect(url_for('auth.login'))

  login_user(user, remember=remember)
  return redirect(url_for('main.profile'))

@auth.route('/signup', strict_slashes=False)
def signup():
  """Route to signup page"""
  return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
  """Route to register user"""
  email = request.form.get('email')
  name = request.form.get('name')
  password = request.form.get('password')

  user = User.query.filter_by(email=email).first()
  if user:
    flash('Email address already exists')
    return redirect(url_for('auth.signup'))
  new_user = User(email=email, name=name,
                  password=generate_password_hash(password, method='sha256'))

  db.session.add(new_user)
  db.session.commit()

  return redirect(url_for('auth.login'))

@auth.route('/upload', strict_slashes=False)
def upload():
    """Route to upload file page."""
    return render_template('upload.html')

@auth.route('/upload', methods=['POST'])
def uploadFile():
    """Function to save uploaded file. """
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(uploads_dir,
                                 uploaded_file.filename)
        uploaded_file.save(file_path)
        return redirect(url_for('auth.visualize'))

@auth.route('/dashboard', methods=['POST', 'GET'])
def visualize():
    """Route to visualization page."""
    return render_template('visualize.html')
#def visualize(filePath):
 #   csvData = pd.read_csv(filePath, header=0)

@auth.route('/logout')
@login_required
def logout():
  """Route to log out"""
  logout_user()
  return redirect(url_for('main.index'))
