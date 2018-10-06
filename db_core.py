# -*- coding: utf-8 -*-
'''
Created on Fri Aug 25 21:17:05 2017

@author: mnt
'''

import sqlalchemy as sa
import sqlalchemy_utils as sa_util

from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
import enum
import vibrobase as vb
import datetime
import re

Base = declarative_base()




class DBinfo:
    user        = 'pgadmin'
    password    = 'pgadmin'
    database    = 'vibrobase'
    host        = '192.168.42.204'
    port        =  5432
    encoding    = 'utf8'


###############################################################################


class DB_COM:
    '''
    Connect to database
    '''

    def __init__(self, db_info = DBinfo):

        self.info = db_info

        self.url = 'postgresql://{}:{}@{}:{}/{}'
        self.url = self.url.format(self.info.user,
                         self.info.password,
                         self.info.host,
                         self.info.port,
                         self.info.database)


        self.engine = self.connect()


    def connect(self):

        '''
        # Returns a connection and a metadata object
        # We connect with the help of the PostgreSQL URL
        # postgresql://user:password@address:5432/database_name
        # The return value of create_engine() is our connection object
        '''
        engine = sa.create_engine(self.url, client_encoding=self.info.encoding)

        return engine



    def get_meta(self):
        # We then bind the connection to MetaData()
        meta = sa.MetaData(bind=self.engine)
        return meta


    def close(self,session):
        session.close()

    def commit(self,session):
        try:
            session.commit()
        except sa.exc.IntegrityError:
            session.rollback()
            raise
            #print('Integrety Error: Commit Failed, rolling back...')

    def commit_and_close(self,session):
        try:
            session.commit()
        except sa.exc.IntegrityError:
            session.rollback()
            raise
            #print('Integrety Error: Commit Failed, rolling back...')
        finally:
            session.close()



    def session(self):
        '''
        A DBSession() instance establishes all conversations with the database
        and represents a 'staging zone' for all the objects loaded into the
        database session object. Any change made against the objects in the
        session won't be persisted into the database until you call
        session.commit(). If you're not happy about the changes, you can
        revert all of them back to the last commit by calling
        session.rollback()
        '''
        try:
            db_session = sa.orm.sessionmaker(bind=self.engine)
            session = db_session()
            return session
        except:
            #print('Integrety Error: Commit Failed, rolling back...')
            raise



    def __delete_database__(self):

        user_input = str(input("Are you absolutely sure you want to reset the current database? Type 'yes' and hit enter! "))
        if user_input == 'yes':
            sa_util.drop_database(self.engine.url)
            return True
        else:
            return False


    def __create_database__(self):

        if not sa_util.database_exists(self.engine.url):
            sa_util.create_database(self.engine.url)
            return True
        else:
            print('Database already exists... doing nothing!')
            return False

    def __populate_database__(self):

        if sa_util.database_exists(self.engine.url):
            Base.metadata.create_all(self.engine)
            return True
        else:
            print('Database doesnt exists... doing nothing!')
            return False


    def __reset_database__(self):

        deleted = self.__delete_database__()
        if deleted:
            created = self.__create_database__()
            if created:
                self.__populate_database__()

                return True
        return False


###############################################################################



class FreqDistEnum(enum.Enum):
    lin = 'lin'
    log = 'log'



class User(Base):

    __tablename__ 			= 	'user'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    username                =   sa.Column(sa.String, nullable=False)
    alias               	=   sa.Column(sa.String, unique=True, nullable=False)
    created             	=   sa.Column(sa.DateTime)
    email               	=   sa.Column(sa.String)
    phone               	=   sa.Column(sa.String)

    sample_events           =   relationship('Sample_Event', back_populates='user', lazy='dynamic')



    def __init__(self, username, alias = '', email = '', phone = None, created = None):

        if alias == '':
            alias = username.split(' ')[0][0] + ''.join(username.split(' ')[1:])
            alias = alias.lower()

        if email == '':
            email = username.split(' ')[0] + '.' + ''.join(username.split(' ')[1:])
            email = email.lower() + '@vibrosonic.de'

        self.username    = username,
        self.alias   = alias,
        if created is None:
            created = datetime.datetime.now()
        self.created = created,
        self.email   = email,
        self.phone   = phone


    def __repr__(self):
        return '<User (name="%s")>' % (self.username)

ass_table_sample_sample = sa.Table('ass_table_sample_sample', Base.metadata,
    sa.Column('sample_id', sa.Integer, sa.ForeignKey('sample.id'), primary_key=True),
    sa.Column('sample_parent_id', sa.Integer, sa.ForeignKey('sample.id'), primary_key=True))

ass_table_sample_sample_type = sa.Table('ass_table_sample_sample_type', Base.metadata,
    sa.Column('sample_id', sa.Integer, sa.ForeignKey('sample.id'), primary_key=True),
    sa.Column('sample_type_id', sa.Integer, sa.ForeignKey('sample_type.id'), primary_key=True))

ass_table_sample_sample_state = sa.Table('ass_table_sample_sample_state', Base.metadata,
    sa.Column('sample_id', sa.Integer, sa.ForeignKey('sample.id'), primary_key=True),
    sa.Column('sample_state_id', sa.Integer, sa.ForeignKey('sample_state.id'), primary_key=True))


class Sample(Base):
    __tablename__ 			= 	'sample'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    samplename              =   sa.Column(sa.String(), unique=True, nullable=False)
    comment             	=   sa.Column(sa.Text)

    sample_types            =   relationship('Sample_Type',
                                             secondary=ass_table_sample_sample_type,
                                             back_populates='samples')

    sample_states           =   relationship('Sample_State',
                                             secondary=ass_table_sample_sample_state,
                                             back_populates='samples')

    sample_events           =   relationship('Sample_Event', back_populates='sample', lazy='dynamic')
    parents                 =   relationship('Sample',
                                             secondary=ass_table_sample_sample,
                                             primaryjoin=id==ass_table_sample_sample.c.sample_id,
                                             secondaryjoin=id==ass_table_sample_sample.c.sample_parent_id,
                                             backref='children')

    def __init__(self,
                 user,
                 samplename,
                 comment,
                 sample_types,
                 sample_states = 'default',
                 parents = None,
                 session = None):


        if session is not None:
            user                = vb.db_tools.get_user(session, user)
            creation_event_type = vb.db_tools.get_sample_event_type(session, 'creation')

        str = ''
        samplename = str.join(samplename)
        samplename          = samplename.upper()
        self.samplename     = samplename
        self.comment        = comment

        # associate sample with sample states
        if sample_states:
            if type(sample_states) is not list: sample_states = [sample_states]

            for sample_state in sample_states:
                if session is not None: sample_state = sample_state(name=vb.db_tools.get_sample_state(session, sample_state).first())
                self.sample_states.append(sample_state)


        # associate sample with sample types
        if sample_types:
            if type(sample_types) is not list: sample_types = [sample_types]

            for sample_type in sample_types:
                if session is not None: sample_type = vb.db_tools.get_sample_type(session, sample_type)
                if not re.match(sample_type.regular_expression, samplename):
                    session.rollback()
                    raise ValueError('Sample name does not match sample type\'s regular expression (' + sample_type.regular_expression + ')')

                self.sample_types.append(sample_type)

        else:
            raise ValueError('No sample type has been specified!')

        # maybe the sample has some parents, associate them here
        if parents is not None:
            if type(parents) is not list: parents = [parents]

            for parent in parents:
                if session is not None: parent = vb.db_tools.get_sample(session, parent)

                self.parents.append(parent)

                for ancestor in parent.parents:
                    self.parents.append(ancestor)

        # Add an event to record sample creation
        creation_event      = Sample_Event(
                user                = user,
                sample              = self,
                sample_event_type   = creation_event_type,
                comment             = 'Creation of the sample'
                )

        self.sample_events.append(creation_event)



    def __repr__(self):
        return '<Sample (name="%s")>' % (self.samplename)


class Sample_Type(Base):

    __tablename__ 			= 	'sample_type'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    typename                =   sa.Column(sa.String, nullable=False, unique=True)
    regular_expression      =   sa.Column(sa.String())
    comment             	=   sa.Column(sa.Text)
    samples                 =   relationship('Sample',
                                             secondary=ass_table_sample_sample_type,
                                             back_populates='sample_types',
                                             lazy='dynamic')

    def __repr__(self):
        return '<Sample Type (name="%s")>' % (self.typename)


class Sample_State(Base):

    __tablename__ 			= 	'sample_state'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    statename               =   sa.Column(sa.String, nullable=False)
    specific             	=   sa.Column(sa.String)
    comment            		=   sa.Column(sa.Text)

    samples                 =   relationship('Sample',
                                             secondary=ass_table_sample_sample_state,
                                             back_populates='sample_states',
                                             lazy='dynamic')

    def __repr__(self):
        return '<Sample state (name="%s")>' % (self.statename)


class Sample_Event(Base):

    __tablename__ 			= 	'sample_event'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    user_id            		=   sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    sample_id          		=   sa.Column(sa.Integer, sa.ForeignKey('sample.id'))
    sample_event_type_id 	=   sa.Column(sa.Integer, sa.ForeignKey('sample_event_type.id'))
    timestamp           	=   sa.Column(sa.DateTime)
    state_active            =  	sa.Column(sa.Boolean, nullable=False, default=True)
    comment             	=   sa.Column(sa.Text)
    attachment_id     	    =   sa.Column(sa.Integer, sa.ForeignKey('attachment.id'))
    prev_id 			    =   sa.Column(sa.Integer, sa.ForeignKey('sample_event.id'))

    sample                  =   relationship('Sample', back_populates='sample_events')
    sample_event_type       =   relationship('Sample_Event_Type', back_populates='sample_events')
    measurement_series      =   relationship('Measurement_Series', back_populates='sample_event')
    measurements            =   relationship('Measurement', back_populates='sample_event')
    attachment              =   relationship('Attachment')
    user                    =   relationship('User', back_populates='sample_events')
    prev                    =   relationship('Sample_Event',
                                             uselist        =False,
                                             remote_side    =[id],
                                             backref        = 'next')

    def __init__(self,
                 user,
                 sample,
                 sample_event_type,
                 timestamp      = datetime.datetime.now(),
                 state_active   = True,
                 comment        = '',
                 attachment     = None,
                 prev           = None,
                 session        = None):

        if session is not None:
            user                = vb.db_tools.get_user(session, user)
            sample              = vb.db_tools.get_sample(session, sample)
            sample_event_type   = vb.db_tools.get_sample_event_type(session, sample_event_type)


        self.user               = user
        self.sample             = sample
        self.sample_event_type  = sample_event_type
        self.timestamp          = timestamp
        self.state_active       = state_active
        self.state_active       = state_active
        self.comment            = comment

        if attachment is not None:  self.attachment = attachment
        if prev is not None:        self.prev = prev



    def __repr__(self):
        return '<Event of sample "%s" of type "%s" created by user "%s">' % (self.sample.samplename,
                                                                             self.sample_event_type.eventtypename,
                                                                             self.user.username)



class Sample_Event_Type(Base):

    __tablename__ 			= 	'sample_event_type'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    eventtypename     		=   sa.Column(sa.String, nullable=False, unique=True)
    comment            		=   sa.Column(sa.Text)
    frequent_event     		=   sa.Column(sa.Boolean, nullable=False, default=False)

    sample_events           =   relationship('Sample_Event', back_populates='sample_event_type', lazy='dynamic')

    def __repr__(self):
        return '<Sample Event Type (name="%s")>' % (self.eventtypename)


class Attachment(Base):

    __tablename__ 			= 	'attachment'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    data                	=   sa.Column(sa.Binary, nullable=False)
    filename       	        =   sa.Column(sa.String, nullable=False)
    filetype                =   sa.Column(sa.String)

    def __init__(self,
                 data,
                 filename,
                 filetype = None):

        self.data = data
        self.filename = filename
        self.filetype = filetype


    def __repr__(self):
        return '<Attachment (file name="%s")>' % (self.filename)



class Measurement_Type(Base):

    __tablename__ 			= 	'measurement_type'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    meastypename            =   sa.Column(sa.String, nullable=False, unique=True)
    comment             	=   sa.Column(sa.Text)

    measurement_series      =   relationship('Measurement_Series', back_populates='measurement_type', lazy='dynamic')


    def __repr__(self):
        return '<Measurement Type (name="%s")>' % (self.meastypename)


class Measurement_Series(Base):

    __tablename__ 			= 	'measurement_series'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    measurement_type_id 	=   sa.Column(sa.Integer, sa.ForeignKey('measurement_type.id'), nullable=False)
    sample_event_id     	=   sa.Column(sa.Integer, sa.ForeignKey('sample_event.id'), nullable=False)
    comment             	=   sa.Column(sa.Text)

    measurement_type        =   relationship('Measurement_Type', back_populates='measurement_series')
    measurements            =   relationship('Measurement', back_populates='measurement_series', lazy='dynamic')
    sample_event            =   relationship('Sample_Event', back_populates='measurement_series')

    sample                  =   relationship('Sample',
                                             secondary      = 'sample_event',
                                             primaryjoin    = 'Measurement_Series.sample_event_id == Sample_Event.id',
                                             secondaryjoin  = 'Sample_Event.sample_id == Sample.id',
                                             viewonly       = True)

    def __repr__(self):
        return '<Measurement Series>'


    def __init__(self,
                 user,
                 sample,
                 measurement_type,
                 comment    = '',
                 timestamp  = datetime.datetime.now(),
                 session    = None):


        if session is not None:
            user                = vb.db_tools.get_user(session, user)
            sample              = vb.db_tools.get_sample(session, sample)
            measurement_type    = vb.db_tools.get_measurement_type(session, measurement_type)
            series_event_type   = vb.db_tools.get_sample_event_type(session, 'measurement_series')

        self.comment            = comment
        self.measurement_type   = measurement_type


        # Add an event to record new measurement series
        self.sample_event           = Sample_Event(
                user                = user,
                sample              = sample,
                sample_event_type   = series_event_type,
                comment             = 'New measurement series (' + measurement_type.meastypename + ')',
                timestamp           = timestamp
                )


class Measurement(Base):

    __tablename__ 			= 	'measurement'

    id                      =   sa.Column(sa.Integer, primary_key=True)
    measurement_series_id   =   sa.Column(sa.Integer, sa.ForeignKey('measurement_series.id'), nullable=False)
    sample_event_id         =   sa.Column(sa.Integer, sa.ForeignKey('sample_event.id'), nullable=False)
    variation_parameter     =   sa.Column(sa.String)
    variation_value        	=   sa.Column(sa.String)
    comment                 =   sa.Column(sa.Text)

    measurement_series      =   relationship('Measurement_Series', back_populates='measurements')
    smu_measurement         =   relationship('SMU_Measurement', back_populates='measurement')
    lcr_measurement         =   relationship('LCR_Measurement', back_populates='measurement')
    sample_event            =   relationship('Sample_Event', back_populates='measurements')

    def __init__(self,
                 user,
                 measurement_series,
                 sample,
                 variation_parameter    = '',
                 variation_value        = '',
                 sample_event_type      = 'measurement',
                 comment                = '',
                 timestamp              = datetime.datetime.now(),
                 session                = None):

        if session is not None:
            with session.no_autoflush:
                user                = vb.db_tools.get_user(session, user)
                sample              = vb.db_tools.get_sample(session, sample)
                measurement_series  = vb.db_tools.get_measurement_series(session, measurement_series)
                sample_event_type   = vb.db_tools.get_sample_event_type(session, sample_event_type)

        self.measurement_series = measurement_series
        self.variation_parameter= variation_parameter
        self.variation_value    = variation_value
        self.comment            = comment



        self.sample_event           = Sample_Event(
                user                = user,
                sample              = sample,
                sample_event_type   = sample_event_type,
                comment             = sample_event_type.comment +' ('+ variation_parameter +': '+ variation_value +')',
                timestamp           = timestamp
                )


    def __repr__(self):
        return '<Measurement>'



class LCR_Measurement(Base):

    __tablename__ 			= 	'lcr_meas'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    measurement_id      	=   sa.Column(sa.Integer, sa.ForeignKey('measurement.id'), nullable=False)
    lcr_config_id       	=   sa.Column(sa.Integer, sa.ForeignKey('lcr_config.id'), nullable=False)
    data                	=   sa.Column(sa.ARRAY(sa.Float))

    # primary relationships
    measurement             =   relationship('Measurement', back_populates='lcr_measurement')
    lcr_config              =   relationship('LCR_Configuration', back_populates='lcr_measurements')

    measurement_series      =   relationship('Measurement_Series',
                                             secondary      = 'measurement',
                                             primaryjoin    = 'LCR_Measurement.measurement_id == Measurement.id',
                                             secondaryjoin  = 'Measurement.measurement_series_id == Measurement_Series.id',
                                             viewonly       = True)

    sample_event            =   relationship('Sample_Event',
                                             secondary      = 'measurement',
                                             primaryjoin    = 'LCR_Measurement.measurement_id == Measurement.id',
                                             secondaryjoin  = 'Measurement.sample_event_id == Sample_Event.id',
                                             viewonly       = True)

    def __init__(self,
                 measurement,
                 data,
                 lcr_config,
                 variation_parameter    = '',
                 variation_value        = '',
                 comment                = '',
                 sample_event_type      = 'lcr_measurement',
                 session                = None):


        if session is not None:
            lcr_config          = vb.db_tools.get_lcr_config(session, lcr_config)
            sample_event_type   = vb.db_tools.get_sample_event_type(session, sample_event_type)

        self.measurement        = measurement
        self.lcr_config         = lcr_config
        self.data               = data

    def __repr__(self):
        return '<LCR_Measurement>'



class SMU_Measurement(Base):

    __tablename__ 			= 	'smu_meas'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    measurement_id      	=   sa.Column(sa.Integer, sa.ForeignKey('measurement.id'), nullable=False)
    smu_config_id       	=   sa.Column(sa.Integer, sa.ForeignKey('smu_config.id'), nullable=False)
    resistance_mean     	=   sa.Column(sa.Float)
    resistance_std      	=   sa.Column(sa.Float)

    # primary relationships
    measurement             =   relationship('Measurement', back_populates='smu_measurement')
    smu_config              =   relationship('SMU_Configuration', back_populates='smu_measurements')

    measurement_series      =   relationship('Measurement_Series',
                                             secondary      = 'measurement',
                                             primaryjoin    = 'SMU_Measurement.measurement_id == Measurement.id',
                                             secondaryjoin  = 'Measurement.measurement_series_id == Measurement_Series.id',
                                             viewonly       = True)

    sample_event            =   relationship('Sample_Event',
                                             secondary      = 'measurement',
                                             primaryjoin    = 'SMU_Measurement.measurement_id == Measurement.id',
                                             secondaryjoin  = 'Measurement.sample_event_id == Sample_Event.id',
                                             viewonly       = True)


    def __init__(self,
                 measurement,
                 resistance_mean,
                 resistance_std,
                 smu_config,
                 variation_parameter    = '',
                 variation_value        = '',
                 comment                = '',
                 sample_event_type      = 'smu_measurement',
                 session                = None):


        if session is not None:
            smu_config          = vb.db_tools.get_smu_config(session, smu_config)
            sample_event_type   = vb.db_tools.get_sample_event_type(session, sample_event_type)

        self.measurement        = measurement
        self.smu_config         = smu_config
        self.resistance_mean    = resistance_mean
        self.resistance_std     = resistance_std

        # Add an event to record new measurement series
#        with session.no_autoflush:
#            self.measurement            = Measurement(
#                    user                = user,
#                    measurement_series  = measurement_series,
#                    sample              = series_event.sample,
#                    variation_parameter = variation_parameter,
#                    variation_value     = variation_value,
#                    sample_event_type   = sample_event_type,
#                    comment             = comment,
#                    session             = session
#                    )
#        print(self.measurement.id)

    def __repr__(self):
        return '<SMU_Measurement>'


class LDV_Measurement(Base):

    __tablename__ 			= 	'ldv_meas'

    id              	    =   sa.Column(sa.Integer, primary_key=True)
    measurement_id      	=   sa.Column(sa.Integer, sa.ForeignKey('measurement.id'), nullable=False)
    ldv_config_id       	=   sa.Column(sa.Integer, sa.ForeignKey('ldv_config.id'), nullable=False)
    data                	=   sa.Column(sa.ARRAY(sa.Float))
    graph               	=   sa.Column(sa.Binary)

    def __repr__(self):
        return '<LDV_Measurement>'



class LCR_Configuration(Base):

    __tablename__ 			= 	'lcr_config'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    lcrconfigname           =   sa.Column(sa.String, unique=True, nullable=False)
    user_id             	=   sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    comment             	=   sa.Column(sa.Text)
    config_json         	=   sa.Column(sa.dialects.postgresql.JSONB)
    config_file         	=   sa.Column(sa.Binary)
    source_voltage      	=   sa.Column(sa.Float, nullable=False)
    current_limit       	=   sa.Column(sa.Float)
    freq_min            	=   sa.Column(sa.Float, nullable=False)
    freq_max            	=   sa.Column(sa.Float, nullable=False)
    freq_steps          	=   sa.Column(sa.Integer, nullable=False)
    freq_dist           	=   sa.Column(sa.Enum(FreqDistEnum), nullable=False)
    bias_on           	    =   sa.Column(sa.Boolean, nullable=False, default=False)
    bias_voltage           	=   sa.Column(sa.Float, nullable=False, default=0)
    bias_current_limit     	=   sa.Column(sa.Float, nullable=False, default=0)

    user                    =   relationship('User', backref='lcr_config')
    lcr_measurements        =   relationship('LCR_Measurement', back_populates='lcr_config')


    def __init__(self,
                 lcrconfigname,
                 user,
                 source_voltage,
                 current_limit          = 0.01,
                 freq_min               = 100,
                 freq_max               = 100000,
                 freq_steps             = 52,
                 freq_dist              = 'log',
                 bias_on                = False,
                 bias_voltage           = 0,
                 bias_current_limit     = 0,
                 comment                = 'some lcr configuration',
                 config_json            = '',
                 config_file            = None,
                 session = None):

        if session is not None:
            user = vb.db_tools.get_user(session, user)

        self.lcrconfigname      = lcrconfigname
        self.user             	= user
        self.comment            = comment
        self.config_json        = config_json
        self.config_file        = config_file
        self.source_voltage     = source_voltage
        self.current_limit      = current_limit
        self.freq_min           = freq_min
        self.freq_max           = freq_max
        self.freq_steps         = freq_steps
        self.freq_dist          = freq_dist
        self.bias_on           	= bias_on
        self.bias_voltage     	= bias_voltage
        self.bias_current_limit = bias_current_limit

    def __repr__(self):
        return '<LCR_Configuration (name="%s")>' % (self.lcrconfigname)



class SMU_Configuration(Base):

    __tablename__ 			= 	'smu_config'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    smuconfigname         	=   sa.Column(sa.String, unique=True, nullable=False)
    user_id             	=   sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    comment             	=   sa.Column(sa.Text)
    config_json         	=   sa.Column(sa.dialects.postgresql.JSONB)
    config_file         	=   sa.Column(sa.Binary)
    meas_lag            	=   sa.Column(sa.Float, nullable=False)
    source_voltage      	=   sa.Column(sa.Float, nullable=False)
    current_limit       	=   sa.Column(sa.Float)
    averages            	=   sa.Column(sa.Integer, default=1)

    user                    =   relationship('User', backref='smu_config')
    smu_measurements        =   relationship('SMU_Measurement', back_populates='smu_config')

    def __init__(self,
                 smuconfigname,
                 user,
                 source_voltage,
                 current_limit        = 0.01,
                 meas_lag             = 0.5,
                 averages             = 5,
                 comment              = 'some smu configuration',
                 config_json          = '',
                 config_file          = None,
                 session = None):

        if session is not None:
            user = vb.db_tools.get_user(session, user)

        self.smuconfigname   =   smuconfigname
        self.user            =   user
        self.comment         =   comment
        self.config_json     =   config_json
        self.config_file     =   config_file
        self.meas_lag        =   meas_lag
        self.source_voltage  =   source_voltage
        self.current_limit   =   current_limit
        self.averages        =   averages


    def __repr__(self):
        return '<SMU_Configuration (name="%s")>' % (self.smuconfigname)

class LDV_Configuration(Base):

    __tablename__ 			= 	'ldv_config'

    id                  	=   sa.Column(sa.Integer, primary_key=True)
    ldvconfigname           =   sa.Column(sa.String, unique=True, nullable=False)   # Descriptive name
    user_id             	=   sa.Column(sa.Integer, sa.ForeignKey('user.id'))     # User that initially created this config. Not necessairly the measuring user
    comment             	=   sa.Column(sa.Text)                                  # Description
    config_json         	=   sa.Column(sa.dialects.postgresql.JSONB)             # The ldv.settings class as json
    config_file_oszi    	=   sa.Column(sa.Binary)                                # The binary settings file from the oszi
    config_file_fg      	=   sa.Column(sa.Binary)                                # The binary settings file from the function generator
    config_file_ldv     	=   sa.Column(sa.Binary)                                # The binary settings file from the ldv
    sweep_type          	=   sa.Column(sa.String, nullable=False)
    acquisition_time    	=   sa.Column(sa.ARRAY(sa.Float), nullable=False)
    averages            	=   sa.Column(sa.Integer, nullable=False)
    frequencies         	=   sa.Column(sa.ARRAY(sa.Integer), nullable=False)
    source_voltages     	=   sa.Column(sa.ARRAY(sa.Float), nullable=False)
    version             	=   sa.Column(sa.Text)

    user                    =   relationship('User', backref='ldv_config')

    def __init__(self,
                 ldvconfigname,
                 user,
                 sweep_type,
                 acquisition_time,
                 averages,
                 frequencies,
                 source_voltages,
                 comment              = 'some ldv configuration',
                 config_json          = '',
                 config_file_oszi     = None,
                 config_file_fg       = None,
                 config_file_ldv      = None,
                 version              = '',
                 session = None):

        if session is not None:
            user = vb.db_tools.get_user(session, user)

        self.ldvconfigname      =   ldvconfigname
        self.user               =   user
        self.sweep_type         =   sweep_type
        self.acquisition_time   =   acquisition_time
        self.averages           =   averages
        self.frequencies        =   frequencies
        self.source_voltages    =   source_voltages
        self.comment            =   comment
        self.config_json        =   config_json
        self.config_file_oszi   =   config_file_oszi
        self.config_file_fg     =   config_file_fg
        self.config_file_ldv    =   config_file_ldv
        self.version            =   version


    def __repr__(self):
        return '<LDV_Configuration (name="%s")>' % (self.ldvconfigname)

#####
'''
if False:
    db_com = DB_COM(DBinfo)
    Base.metadata.create_all(db_com.engine)
'''
