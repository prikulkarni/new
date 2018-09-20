from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
#from data import Articles
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from wtforms import Form, StringField, TextField, TextAreaField, PasswordField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from passlib.hash import sha256_crypt
from functools import wraps
from db_core import DB_COM, Base, Sample, Sample_Type, Sample_State

import json
import plotly
import db_core as db_core

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:linux123@localhost/vibrobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change'
db = SQLAlchemy(app)
session = DB_COM.session(db)


# class Sample(db.Model):
#     __tablename__ = "sample"
#     id = db.Column(db.Integer, primary_key=True)
#     samplename = db.Column(db.String, nullable=False)
#     comment = db.Column(db.Text, nullable=False)
#
#     def __init__(self, sample_name, comment):
#         self.samplename =  samplename
#         self.comment = comment
#
#     def __repr__(self):
#         return '<id {}>'.format(self.id)

class ReadOnlyTextField( TextField ):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadOnlyTextField, self).__call__(*args, **kwargs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse_samples')
def browse_samples():
    #Get the list of sample events for a sample
    samples = session.query(Sample).all()

    if (samples != None):
        return render_template('browse_samples.html', samples=samples)
    else:
        msg = "No samples yet"
        return render_template('browse_samples.html', msg=msg)

def get_sample_types():
    sample_types = session.query(Sample_Type).all()
    return sample_types

def get_sample_states():
    sample_states = session.query(Sample_State).all()
    return sample_states

def get_parents():
    parents = session.query(Sample).all()
    return parents

#Add Sample Form Class
class AddSampleForm(Form):
    samplename = StringField('Name', [validators.Length(min=1, max=20)])
    typename = QuerySelectField ('Sample Type', [validators.Required()], query_factory = get_sample_types, get_label = 'typename' )
    statename = QuerySelectField ('Sample State', [validators.Required()], query_factory = get_sample_states, get_label = 'statename' )
    select_parents = QuerySelectField ('Select Parents', allow_blank = True, query_factory = get_parents, get_label = 'samplename' )
    parents = ReadOnlyTextField ('Selected Parents')
    comment = TextAreaField('Comment', [validators.Length(min=1)])

@app.route('/add_sample', methods=['GET', 'POST'])
def add_sample():
    #Get form
    form = AddSampleForm(request.form)
    #Populate selected parents
    #form.parents.data = form.select_parents.data
    if request.method == 'POST' and form.validate():
        samplename      = request.form['samplename'],
        sample_types    = request.form['typename'],
        sample_states   = request.form['statename'],
        parents         = request.form['parents'],
        comment         = request.form['comment'],
        user            = 'Default'
        samp = Sample (user, samplename, comment, sample_types, sample_states)
        session.add(samp)
        session.commit()

        flash('Sample Added','success')

    return render_template('add_sample.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
