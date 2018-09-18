# -*- coding: utf-8 -*-
'''
Created on Fri Aug 25 21:17:05 2017

@author: mnt
'''


#import datetime
#import re
from string import ascii_uppercase

#from vibrobase import db_core as db
import db_core as db

###############################################################################
### SAMPLE
###############################################################################

def get_sample(session, sample):

    if type(sample) is db.Sample:
        pass
    elif type(sample) is str:
        sample = session.query(db.Sample).filter_by(samplename = sample).first()
    elif type(sample) is int:
        sample = session.query(db.Sample).filter_by(id = sample).first()
    else:
        sample = None

    return sample


def list_sample(session, parents = '*', sample_types = '*', sample_states = '*'):

    if sample_states is None or sample_types is None: return None

    query = session.query(db.Sample)

    if type(parents) is not list: parents = [parents]
    #if None in parents: return None
    parents = list(filter(('*').__ne__, parents)) #remove all '*' from the list
    if parents != []:
        parent_ids      = []
        for parent in parents:
            parent = get_sample(session, parent)
            if parent is not None: parent_ids.append(parent.id)

#        parent_ids      = [get_sample(session, parent).id for parent in parents]
        query           = query.filter(db.Sample.parents.any(db.Sample.id.in_(parent_ids)))
#        query           = query.filter(db.Sample.parents.any(db.Sample.id.in_(parent_ids)))
#        parent          = get_sample(session, parent)
#        query           = query.filter(db.Sample.parents.any(id = parent.id))

    if type(sample_types) is not list: sample_types = [sample_types]
    if '*' in sample_types: sample_types.remove('*')
    if sample_types != []:
        sample_type_ids = [get_sample_type(session, sample_type).id for sample_type in sample_types]
        query           = query.filter(db.Sample.sample_types.any(db.Sample_Type.id.in_(sample_type_ids)))
#        sample_type 		= get_sample_type(session, sample_type)
#        query           = query.filter(db.Sample.sample_type.any(id = sample_type.id))

    if type(sample_states) is not list: sample_states = [sample_states]
    if '*' in sample_states: sample_states.remove('*')
    if sample_states != []:
        sample_state_ids = [get_sample_state(session, sample_state).id for sample_state in sample_states]
        query           = query.filter(db.Sample.sample_states.any(db.Sample_State.id.in_(sample_state_ids)))
#        sample_state 		= get_sample_state(session, sample_state)
#        query           = query.filter(db.Sample.sample_state == sample_state.id)

    samples = query.all()

    return samples

###############################################################################
### SAMPLE TYPE
###############################################################################

def get_sample_type(session, sample_type):

    if type(sample_type) is db.Sample_Type:
        pass
    elif type(sample_type) is str:
        sample_type = session.query(db.Sample_Type).filter_by(typename = sample_type).first()
    elif type(sample_type) is int:
        sample_type = session.query(db.Sample_Type).filter_by(id = sample_type).first()
    else:
        sample_type = None

    return sample_type

def list_sample_type(session):

    sample_types = session.query(db.Sample_Type).all()

    return sample_types


###############################################################################
### SAMPLE STATE
###############################################################################

def get_sample_state(session, sample_state):

    if type(sample_state) is db.Sample_State:
        pass
    elif type(sample_state) is str:
        sample_state = session.query(db.Sample_State).filter_by(statename = sample_state).first()
    elif type(sample_state) is int:
        sample_state = session.query(db.Sample_State).filter_by(id = sample_state).first()
    else:
        sample_state = None

    return sample_state

def list_sample_state(session):

    sample_states = session.query(db.Sample_State).all()

    return sample_states


###############################################################################
### USER
###############################################################################

def get_user(session, user):

    if type(user) is db.User:
        pass
    elif type(user) is str:
        user_name = user
        user = session.query(db.User).filter_by(username = user_name).first()
        if user is None:
            user = session.query(db.User).filter_by(alias = user_name).first()
    elif type(user) is int:
        user = session.query(db.User).filter_by(id = user).first()
    else:
        user = None

    return user

def list_user(session):

    users = session.query(db.User).all()

    return users

###############################################################################


def list_sample_event(session,
                      user              = '*',
                      sample            = '*',
                      sample_event_type = '*',
                      time_after        = '*',
                      time_before       = '*',
                      state_active      = True,
                      frequent_event    = False,
                      has_attachment    = '*', #make it bool or '*'
                      prev              = '*',
                      next              = '*',
                      any_prev          = '*',
                      any_next          = '*'
                      ):

    if None in [user, sample, sample_event_type]:
        return None

    query = session.query(db.Sample_Event)


    if user != '*':
        user                = get_user(session, user)
        query               = query.filter(db.Sample_Event.user.any(id = user.id))

    if sample != '*':
        sample              = get_sample(session, sample)
        query               = query.filter(db.Sample_Event.sample.any(id = sample.id))

    if sample_event_type != '*':
        sample_event_type   = get_sample_event_type(session, sample_event_type)
        query               = query.filter(db.Sample_Event.sample_event_type.any(id = sample_event_type.id))

    if time_after != '*':
        query               = query.filter(db.Sample_Event.timestamp >= time_after)

    if time_before != '*':
        query               = query.filter(db.Sample_Event.timestamp <= time_before)

    if has_attachment != '*':
        if has_attachment is True:
            query           = query.filter(db.Sample_Event.attachment != None)
        elif has_attachment is False:
            query           = query.filter(db.Sample_Event.attachment == None)

    if prev != '*':
        query               = query.filter(db.Sample_Event.prev == prev)

    if next != '*':
        query               = query.filter(db.Sample_Event.next == next)

    ### TODO: implement search of the entire family tree here for any_prev and any_next

    sample_events = query.filter(db.Sample_Event.state_active == state_active).all()

    return sample_events


###############################################################################


def get_sample_event_type(session, sample_event_type):

    if type(sample_event_type) is db.Sample_Event_Type:
        pass
    elif type(sample_event_type) is str:
        sample_event_type = session.query(db.Sample_Event_Type).filter_by(eventtypename = sample_event_type).first()
    elif type(sample_event_type) is int:
        sample_event_type = session.query(db.Sample_Event_Type).filter_by(id = sample_event_type).first()
    else:
        sample_event_type = None

    return sample_event_type

def list_sample_event_type(session):

    event_types = session.query(db.Sample_Event_Type).all()

    return event_types

###############################################################################

def get_measurement_type(session, measurement_type):

    if type(measurement_type) is db.Measurement_Type:
        pass
    elif type(measurement_type) is str:
        measurement_type = session.query(db.Measurement_Type).filter_by(meastypename = measurement_type).first()
    elif type(measurement_type) is int:
        measurement_type = session.query(db.Measurement_Type).filter_by(id = measurement_type).first()
    else:
        measurement_type = None

    return measurement_type

###############################################################################

def get_measurement_series(session, measurement_series):

    if type(measurement_series) is db.Measurement_Series:
        pass
    elif type(measurement_series) is int:
        measurement_series = session.query(db.Measurement_Series).filter_by(id = measurement_series).first()
    else:
        measurement_series = None

    return measurement_series



###############################################################################

def get_smu_config(session, smu_config):

    if type(smu_config) is db.SMU_Configuration:
        pass
    elif type(smu_config) is str:
        smu_config = session.query(db.SMU_Configuration).filter_by(smuconfigname = smu_config).first()
    elif type(smu_config) is int:
        smu_config = session.query(db.SMU_Configuration).filter_by(id = smu_config).first()
    else:
        smu_config = None

    return smu_config

###############################################################################

def get_lcr_config(session, lcr_config):

    if type(lcr_config) is db.LCR_Configuration:
        pass
    elif type(lcr_config) is str:
        lcr_config = session.query(db.LCR_Configuration).filter_by(lcrconfigname = lcr_config).first()
    elif type(lcr_config) is int:
        lcr_config = session.query(db.LCR_Configuration).filter_by(id = lcr_config).first()
    else:
        lcr_config = None

    return lcr_config


###############################################################################

def get_ldv_config(session, ldv_config):

    if type(ldv_config) is db.LDV_Configuration:
        pass
    elif type(ldv_config) is str:
        ldv_config = session.query(db.LDV_Configuration).filter_by(ldvconfigname = ldv_config).first()
    elif type(ldv_config) is int:
        ldv_config = session.query(db.LDV_Configuration).filter_by(id = ldv_config).first()
    else:
        ldv_config = None

    return ldv_config
