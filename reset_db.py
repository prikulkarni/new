# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 21:17:05 2017

@author: mnt
"""

#from vibrobase import db_core as db
import db_core as db
import datetime
#import json
import db_tools

db_com = db.DB_COM(db.DBinfo)

''' RESET DATABASE '''
# This deletes all data in the database
# ...will prompt for user input to perform reset
if True:
    db_com.__reset_database__()

if True:
    MAKE_USERS                  = True
    MAKE_DESIGNS                = True
    MAKE_BATCHES                = True
    MAKE_SAMPLES                = True
    MAKE_SAMPLE_TYPES           = True
    MAKE_SAMPLE_EVENT_TYPES     = True
    MAKE_MEASUREMENT_TYPES      = True
    MAKE_SMU_CONFIG             = True
    MAKE_LCR_CONFIG             = True
    MAKE_LDV_CONFIG             = True
    MAKE_SAMPLE_STATE           = True

else:
    MAKE_USERS                  = False
    MAKE_DESIGNS                = False
    MAKE_BATCHES                = False
    MAKE_SAMPLES                = False
    MAKE_SAMPLE_TYPES           = False
    MAKE_SAMPLE_EVENT_TYPES     = False
    MAKE_MEASUREMENT_TYPES      = False
    MAKE_SMU_CONFIG             = False
    MAKE_LCR_CONFIG             = False
    MAKE_LDV_CONFIG             = False
    MAKE_SAMPLE_STATE           = False



if MAKE_USERS is True:
    new_user_list = []


    new_user_list.append(db.User(username = 'Dominik Kaltenbacher',
         created = datetime.datetime.now(),
         alias = 'dkaltenbacher'))

    new_user_list.append(db.User(username = 'Jonathan Schächtele',
         created = datetime.datetime.now(),
         alias = 'jschaechtele'))

    new_user_list.append(db.User(username = 'Tobias Fritzsche',
         created = datetime.datetime.now(),
         alias = 'tfritzsche'))

    new_user_list.append(db.User(username = 'Florian Strobl',
         created = datetime.datetime.now(),
         alias = 'fstrobl'))

    new_user_list.append(db.User(username = 'Martin Theuring',
         created = datetime.datetime.now(),
         alias = 'mtheuring'))

    session = db_com.session()
    session.add_all(new_user_list)

    db_com.commit_and_close(session)


if MAKE_SAMPLE_EVENT_TYPES is True:
    new_sample_event_type_list = []

    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = '_default',
            comment         = 'Default event for arbitrary entries'))
    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = 'creation',
            comment         = 'A new sample is being created'))
    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = 'measurement_series',
            comment         = 'New measurement series'))
    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = 'measurement',
            comment         = 'Measuring',
            frequent_event  = True))
    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = 'smu_measurement',
            comment         = 'Measuring with SMU',
            frequent_event  = True))
    new_sample_event_type_list.append(db.Sample_Event_Type(
            eventtypename   = 'lcr_measurement',
            comment         = 'Measuring with LCR Meter',
            frequent_event  = True))

    session = db_com.session()
    session.add_all(new_sample_event_type_list)
    db_com.commit_and_close(session)


if MAKE_SAMPLE_TYPES is True:
    new_type_list = []

    new_type_list.append(db.Sample_Type(
            typename                = '_DEFAULT',
            regular_expression      = '^[A-Z,0-9]{1,}[A-Z,0-9,\-]*$',
            comment                 = 'This is the default sample type'))

    new_type_list.append(db.Sample_Type(
            typename                = 'mask set',
            regular_expression      = '^[A]{1}[0-9]{2}$',
            comment = 'Sample type for mask sets to fabricate wafer'))

    new_type_list.append(db.Sample_Type(
            typename                = 'electrical component',
            regular_expression      = '^[A]{1}[0-9]{2}$',
            comment = 'Sample type for mask sets to fabricate wafer'))

    new_type_list.append(db.Sample_Type(
            typename                = 'lithography mask',
            regular_expression      = '^[L]{1}[0-9]{2}$',
            comment = 'Sample type for lithography mask'))

    new_type_list.append(db.Sample_Type(
            typename                = 'mechanical component',
            regular_expression      = '^[M]{1}[0-9]{2}$',
            comment = 'Sample type for mask sets to fabricate wafer'))

    new_type_list.append(db.Sample_Type(
            typename                = 'wafer',
            regular_expression      = '^[A]{1}[0-9]{2}[\-][0-9]{6}[A-Z]$',
            comment = 'Sample type for wafer to be broken down into actuators and alike'))

    new_type_list.append(db.Sample_Type(
            typename                = 'die',
            regular_expression      = '^[A]{1}[0-9]{2}[\-][0-9]{6}[A-Z][\-][A-Z0-9]{5}$',
            comment = 'Anything that comes out of a wafer'))

    new_type_list.append(db.Sample_Type(
            typename                = 'actuator',
            regular_expression      = '^[A]{1}[0-9]{2}[\-][0-9]{6}[A-Z][\-][A][A-Z0-9]{4}$',
            comment = 'Sample type for actuators'))



    session = db_com.session()
    session.add_all(new_type_list)
    db_com.commit_and_close(session)


if MAKE_SAMPLE_STATE is True:
    new_type_list = []

    new_type_list.append(db.Sample_State(
            statename   = 'default',
            comment     = 'This is the default sample state'))

    new_type_list.append(db.Sample_State(
            statename   = 'damaged',
            specific    = 'shorted',
            comment     = 'Sample is shorted'))

    new_type_list.append(db.Sample_State(
            statename   = 'archived',
            specific    = 'storage room',
            comment     = ''))

    new_type_list.append(db.Sample_State(
            statename   = 'in production',
            specific    = 'NMI',
            comment     = ''))


    session = db_com.session()
    session.add_all(new_type_list)
    db_com.commit_and_close(session)


if MAKE_DESIGNS is True:
    new_design_list = []
    session = db_com.session()


    new_design_list.append(db.Sample(
            user          = 'mtheuring',
            samplename    = 'A99',
            comment       = 'This is just a Test Design',
            sample_types  = 'mask set',
            sample_states = 'default',
            parents       = None,
            session       = session
            ))

    session.add_all(new_design_list)
    db_com.commit_and_close(session)



if MAKE_BATCHES is True:

    new_batch_list = []
    session = db_com.session()


    new_batch_list.append(db.Sample(
            user          = 'mtheuring',
            samplename    = 'A99-180111A',
            comment       = 'A Test Wafer',
            sample_types  = 'wafer',
            sample_states = 'default',
            parents       = 'A99',
            session       = session
            ))


    session.add_all(new_batch_list)
    db_com.commit_and_close(session)


if MAKE_MEASUREMENT_TYPES is True:
    new_measurement_type_list = []

    new_measurement_type_list.append(db.Measurement_Type(
            meastypename    = 'default',
            comment         = 'This is the default measurement type, should not be used actually'))

    new_measurement_type_list.append(db.Measurement_Type(
            meastypename    = 'resistance',
            comment         = 'Simple resistance measurement'))


    session = db_com.session()
    session.add_all(new_measurement_type_list)
    db_com.commit_and_close(session)

if MAKE_SAMPLES is True:

    new_sample_list = []
    session = db_com.session()

    new_sample_list.append(db.Sample(
            user          = 'mtheuring',
            samplename    = 'A99-180111A-AX123',
            comment       = 'Test Aktor',
            sample_types  = ['die','actuator'],
            sample_states = 'default',
            parents       = 'A99-180111A',
            session       = session
            ))


    session.add_all(new_sample_list)
    db_com.commit_and_close(session)




if MAKE_SMU_CONFIG is True:

    session = db_com.session()
    new_smu_config = db.SMU_Configuration(
                   smuconfigname    = 'default_config',
                   user             = 'mtheuring',
                   source_voltage   = 0.1,
                   current_limit    = 0.01,
                   averages         = 5,
                   comment          = 'some smu configuration',
                   session = session

                   )

    session.add(new_smu_config)
    db_com.commit_and_close(session)

if MAKE_LCR_CONFIG:

    session = db_com.session()
    new_lcr_config = db.LCR_Configuration(
                lcrconfigname       = 'test-config',
                user                = 'mtheuring',
                source_voltage      = 0.1,
                current_limit       = 0.01,
                freq_min            = 100,
                freq_max            = 100000,
                freq_steps          = 52,
                freq_dist           = 'log',
                bias_on             = False,
                bias_voltage        = 0,
                bias_current_limit  = 0,
                comment             = 'some lcr configuration',
                config_json         = '',
                config_file         = None,
                session             = session
                )

    session.add(new_lcr_config)
    db_com.commit_and_close(session)

if MAKE_LDV_CONFIG:

    session = db_com.session()
    new_ldv_config = db.LDV_Configuration(
                ldvconfigname       = 'test-config',
                user                = 'tfritzsche',
                sweep_type          = 'sweep',
                config_file_oszi    = None,
                acquisition_time    = [1.0],
                averages            = 16,
                frequencies         = [[100,200],[500,700],[1e4,None]],
                source_voltages     = [5],
                comment             = 'a test ldv configuration',
                version             = '101',
                session             = session
                )

    session.add(new_ldv_config)
    db_com.commit_and_close(session)

#
#
#json_config = json.dumps({'source_voltage': 0.1, 'temperature': 25.4, 'Mensa Friday Fish': 'Salmon'})
#parsed_json = json.loads(json_config)
#
#new_configuration = db.SMU_Configuration(
#        name                =   'Standard Resistance Measurement',
#        user                =   user.id,
#        comment             =   'This is something that is to be performed in the case of bla',
#        config_json         =   parsed_json,
#        meas_interval       =   10,
#        source_voltage      =   10.1,
#        freq_steps          =   15
#        )
#
#
#
#''' ADD A SAMPLE EVENT'''
#session = db_com.session()
#new_event = db.SampleEventy(user = user.id,
#                      sample = session.query(db.Sample).filter_by(name='X123').first().id,
#                      timestamp = datetime.datetime.now(),
#                      comment = 'something happened')
#session.add(new_event)
#session.add(new_configuration)
#db_com.commit_and_close(session)
