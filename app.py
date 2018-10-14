from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
#from data import Articles
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import Form
from wtforms import SubmitField, StringField, TextField, TextAreaField, PasswordField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from passlib.hash import sha256_crypt
from functools import wraps
import vibrobase as vb
from vibrobase import db_core
from vibrobase import db_core as db
from vibrobase.db_core import DB_COM, Base, Sample, Sample_Type, Sample_State, Sample_Event
from vibrobase.db_tools import get_sample_event_type
from markupsafe import Markup
import json
import plotly
import pandas as pd
import numpy as np
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:linux123@localhost/vibrobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'change'
db = SQLAlchemy(app)
session = DB_COM.session(db)
app.jinja_env.globals.update(get_sample_event_type=get_sample_event_type)


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
    #Get the list of samples
    samples = session.query(Sample).all()

    if (samples != None):
        return render_template('browse_samples.html', samples=samples)
    else:
        msg = "No samples yet"
        return render_template('browse_samples.html', msg=msg)

def get_samples():
    samples = session.query(Sample).all()
    return samples

class SampleEventsForm(Form):
    select_sample = QuerySelectField ('Select Sample', query_factory = get_samples, get_label = 'samplename' )
    show_events = SubmitField ('Show Events')

@app.route('/select_sample',methods=['GET', 'POST'])
def select_sample():
    form = SampleEventsForm(request.form)
    if request.method == 'POST' or form.validate_on_submit():
        #if form.show_events.data():
        sample = form.select_sample.raw_data
        sample = sample[0]
        #return redirect(url_for('/browse_sample_events/{{sample}}'))
        return render_template('browse_sample_events.html', sample=sample)

    #return render_template('select_sample.html', form=form, sample=sample)
    return render_template('select_sample.html', form=form)

@app.route('/browse_sample_events/<string:sample>',methods=['GET', 'POST'])
def browse_sample_events(sample):
    #Get the list of sample events for a sample
    #form = SampleEventsForm(request.form)
    # query = session.query(db.Sample_Event_Type.eventtypename,db.Sample_Event)\
    #     .filter_by(frequent_event = False)\
    #     .join(db.Sample_Event_Type.sample_events)\
    #     .filter_by(sample_id=sample)\
    #     .filter_by(state_active=True)\
    #     .outerjoin(db.Measurement_Series)\
    #     .outerjoin(db.Measurement_Type)\
    #     .add_column(db.Measurement_Type.meastypename)\
    #     .outerjoin(vb.db.User)\
    #     .add_column(vb.db.User.username)\
    #     .outerjoin(vb.db.Attachment)\
    #     .add_column(vb.db.Attachment.filename).all()
    sample_events = session.query(Sample_Event).filter_by(sample_id=sample).all()
    if (sample_events != None):
        return render_template('browse_sample_events.html', sample_events=sample_events, session=session)
    else:
        msg = "No events for this sample yet"
        return render_template('browse_sample_events.html', msg=msg)
    # return render_template('browse_sample_events.html', form=form)
    #return render_template('browse_sample_events.html', sample_events=sample_events)

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
    typename = QuerySelectField ('Select Sample Type', query_factory = get_sample_types, get_label = 'typename' )
    add_sample_type = SubmitField ('Add Sample Type')
    sample_types = ReadOnlyTextField ('Selected Sample Types')
    statename = QuerySelectField ('Sample State', query_factory = get_sample_states, get_label = 'statename' )
    add_sample_state = SubmitField ('Add Sample State')
    sample_states = ReadOnlyTextField ('Selected Sample States')
    select_parents = QuerySelectField ('Select Parents', allow_blank = True, query_factory = get_parents, get_label = 'samplename' )
    add_parent = SubmitField ('Add Parent')
    parents = ReadOnlyTextField ('Selected Parents')
    comment = TextAreaField('Comment')
    add_sample_value = Markup('Add Sample')
    add_sample = SubmitField (add_sample_value)

@app.route('/add_sample', methods=['GET', 'POST'])
def add_sample():
    #Get form
    form = AddSampleForm(request.form)
    #Populate selected parents
    #form.parents.data = form.select_parents.data
    if request.method == 'POST' and form.validate():
        if form.add_sample.data:
            samplename      = request.form['samplename'],
            sample_types    = request.form['sample_types'],
            sample_state   = request.form['statename'],
            parents         = request.form['parents'],
            comment         = request.form['comment'],
            user            = 'Default'
            samp = Sample (user, samplename, comment, sample_types, sample_state)
            session.add(samp)
            session.commit()

            flash('Sample Added','success')
        elif form.add_parent.data:
            selected_parent = form.select_parents.raw_data
            parents = form.parents.raw_data
            # parents.extend(selected_parent)
            # form.parents.data = parents
            if parents == ['']:
                form.parents.data = selected_parent[0]
            else:
                parents.append(selected_parent[0])
                form.parents.data = parents

        elif form.add_sample_type.data:
            selected_type = form.typename.raw_data
            sample_types = form.sample_types.raw_data
            if sample_types == ['']:
                form.sample_types.data = selected_type[0]
            else:
                sample_types = sample_types + selected_type
                form.sample_types.data = sample_types

        elif form.add_sample_state.data:
            selected_state = form.statename.raw_data
            sample_states = form.sample_states.raw_data
            if sample_states == ['']:
                form.sample_states.data = selected_state[0]
            else:
                sample_states = sample_states[0] + selected_state[0]
                #sample_states = list(map, int(sample_states))
                #sample_states = [y for x in sample_states for y in x]
                #sample_states = [int(x) for x in sample_states]
                form.sample_states.data = sample_states

    return render_template('add_sample.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
