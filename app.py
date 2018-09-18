from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
#from data import Articles
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

import json
import plotly

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:linux123@localhost/vibrobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change'
db = SQLAlchemy(app)

class Sample(db.Model):
    __tablename__ = "sample"
    id = db.Column(db.Integer, primary_key=True)
    samplename = db.Column(db.String, nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, sample_name, comment):
        self.samplename =  samplename
        self.comment = comment

    def __repr__(self):
        return '<id {}>'.format(self.id)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse_samples')
def browse_sample_events():
    #Get the list of sample events for a sample
    samples = Sample.query.all()

    if (samples != None):
        return render_template('browse_samples.html', samples=samples)
    else:
        msg = "No samples yet"
        return render_template('browse_samples.html', msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
