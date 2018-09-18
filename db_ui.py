# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 11:08:17 2018

@author: mtheuring
"""


####################
'''
MAYBE THIS STUFF SHOULD BE CONVERTED TO SOMETHING OBJECT ORIENTED
'''
###

import ipywidgets as widgets
from IPython.display import display
from IPython.display import FileLink

import vibrobase as vb
from vibrobase import db_core as db
from abc import ABC, abstractmethod
import re
import pandas as pd
import numpy as np
import beakerx as bx
import datetime
import plotly.offline as py
import matplotlib.pyplot as plt
import cufflinks as cf
import plotly.graph_objs as go
import fileupload
import os
import time




def show_menu():
    f = bx.EasyForm('MENU')
    f.addButton('Event Browser', tag='sample_events')
    f.addButton('New DB entries', tag='entries')
    f.addButton('Plot SMU data', tag='smu_plot')
    display(f)

##############################################################
################ ABSTRACT CLASSES ############################
##############################################################

class Selector(ABC):
    ''''SELECTOR ABSTRACT CLASS'''
    
    def __init__(self, db_com, description, allow_all = False, multiple = False, remove_from_list = []):
        
        self.db_com             = db_com
        self.allow_all          = allow_all
        self.multiple           = multiple
        self.remove_from_list   = remove_from_list
        
        if self.multiple is True:
            self.wDropdown          = widgets.SelectMultiple(options= self.get_list(), description = description + ':')
        else: 
            self.wDropdown          = widgets.Dropdown(options= self.get_list(), description = description + ':')
            
        self.widget             = self.wDropdown
#        self.update_wButton     = widgets.Button(description='Update',disabled=False,button_style='')
#        self.widget             = widgets.HBox([self.wDropdown, self.update_wButton])
#        self.update_wButton.on_click(self.update_clicked)
    
    def get_list(self):  
        
        list_from_db    = self.query_list()
        list_from_db    = sorted(list_from_db)
        
        if self.allow_all is True:
            list_from_db = ['*'] + list_from_db
        for item in self.remove_from_list:
            list_from_db.remove(item)
            
        return list_from_db
    
    
    def update_clicked(self, b):
        self.update_list()
        
    def update_list(self):
        self.wDropdown.options = self.get_list()
        if len(self.wDropdown.options) == 0:
            
            if self.multiple is True:
                self.wDropdown.value = []
            else:
                self.wDropdown.value = None
        else:
            if self.multiple is True:
                self.wDropdown.value = []
            else:
                self.wDropdown.value = self.wDropdown.options[0]
            

    @abstractmethod
    def query_list(self):
        list_from_db = []
        return list_from_db




class Data_Input(ABC):
    
    def __init__(self, db_com):
        

        self.db_com         = db_com
        self.submit_wButton = widgets.Button(description='Submit',disabled=False,button_style='')
        self.notify_wHTML   = widgets.HTML(value='')

        self.submit_wButton.on_click(self.submit_clicked)

        self.widget         = None


    def set_notify(self, message, color):
        message = '<font color="' + color + '">' + str(message) + ' </font>'
        self.notify_wHTML.value = message


    def submit_clicked(self, b):
        
        try:
            notifier_message = self.data_submission()
            self.set_notify(notifier_message, 'green')
            
        except Exception as e: self.set_notify(e, 'red')

    @abstractmethod
    def data_submission(self):
        pass
        #return 'Something added'

    @abstractmethod
    def update_lists(self):
        pass
        #return 'Something added'





##############################################################
################ SELECTOR CLASSES ############################
##############################################################


    
class Sample_Type_Selector(Selector):
    ''''SAMPLE TYPE'''
    
    def __init__(self,
                 db_com,
                 description        = 'Sample Type',
                 allow_all          = False,
                 multiple           = False,
                 remove_from_list   = []):
        
        super().__init__(db_com, description, allow_all, multiple, remove_from_list)
    
    def query_list(self):        
        session = self.db_com.session()
        sample_type_list = [sample_type.typename for sample_type in vb.list_sample_type(session)]        
        self.db_com.close(session)        
        return sample_type_list

    
class Sample_State_Selector(Selector):
    ''''SAMPLE TYPE'''
    
    def __init__(self,
                 db_com,
                 description        = 'Sample State',
                 allow_all          = False,
                 multiple           = False,
                 remove_from_list   = []):
        
        super().__init__(db_com, description, allow_all, multiple, remove_from_list)
    
    def query_list(self):        
        session = self.db_com.session()
        sample_state_list = [sample_state.statename for sample_state in vb.list_sample_state(session)]        
        self.db_com.close(session)        
        return sample_state_list


class User_Selector(Selector):
    ''''USER'''
    
    def __init__(self,
                 db_com,
                 description = 'User',
                 allow_all = False,
                 multiple = False,
                 remove_from_list = []):
        
        super().__init__(db_com, description, allow_all, multiple, remove_from_list)
    
    def query_list(self):
        
        session = self.db_com.session()
        user_list = [user.username for user in vb.list_user(session)]
        self.db_com.close(session)
        return user_list
    

class Sample_Event_Type_Selector(Selector):
    ''''EVENT TYPE'''
    
    def __init__(self,
                 db_com,
                 description = 'Event Type',
                 allow_all = False,
                 multiple = False,
                 remove_from_list = ['creation']):
        
        super().__init__(db_com, description, allow_all, multiple, remove_from_list)
    
    def query_list(self):
        
        session = self.db_com.session()
        event_type_list = [event_type.eventtypename for event_type in vb.list_sample_event_type(session)]
        self.db_com.close(session)
        return event_type_list
    

class Sample_Selector(Selector):
    ''''SAMPLE TYPE'''
    
    def __init__(self,
                 db_com,
                 description        = 'Sample',
                 parent             = '*',
                 sample_type        = '*',
                 allow_all          = False,
                 multiple           = False,
                 remove_from_list   = []):
        
        # This needs to be defined before calling the super class
        self.parent             = parent
        self.sample_type        = sample_type
                
        super().__init__(db_com, description, allow_all, multiple, remove_from_list)
        
        
    def query_list(self):        
        if self.parent is None:
            sample_list = []
        
        else:
            session = self.db_com.session()
            sample_list = [sample.samplename for sample in vb.list_sample(session,
                           parents = self.parent,
                           sample_types = self.sample_type)]    
            self.db_com.close(session)
            
        return sample_list
            


class Sample_Selector_Filter():
    ''''SAMPLE TYPE'''
    
    def __init__(self,
                 db_com,
                 description = 'Sample:'):
        
        self.db_com             = db_com

        self.filter_wText       = widgets.Text(value='',description='Filter:')
        self.wDropdown          = widgets.Dropdown(options= self.get_list(), description = description)
        
        self.filter_wText.observe(self.filter_change, names = 'value')
        
        self.widget             = widgets.HBox([self.wDropdown,self.filter_wText])

    def filter_change(self, change):
        self.update_list()
        
    def get_list(self):  
        
        list_from_db    = self.query_list()
        list_from_db    = sorted(list_from_db)            
        return list_from_db
    
    def update_list(self):
        self.wDropdown.options = self.get_list()
        if len(self.wDropdown.options) == 0:
            self.wDropdown.value = None
        else:
            self.wDropdown.value = self.wDropdown.options[0]
            
    def query_list(self):
        
        session = self.db_com.session()
        starts_with = self.filter_wText.value
        samples = session.query(db.Sample).filter(db.Sample.samplename.ilike(starts_with+'%')).all()
        sample_list = [sample.samplename for sample in samples]    
        self.db_com.close(session)
        
        return sample_list
         
    
class BrowseFile:
    
    def __init__(self):

        self.plot_wOutput = widgets.Output()
        self._upload_widget = fileupload.FileUploadWidget()
        self._upload_widget.observe(self._cb, names='data')
        self.change = None
        self.data = None
        self.filename = ''
        with self.plot_wOutput:
            display(self._upload_widget)
        self.file_HTML = widgets.HTML(value=None)
        self.Attachment_HTML = widgets.HTML(value='Attachment:')
        
        self.widget = widgets.HBox([self.Attachment_HTML, self.plot_wOutput, self.file_HTML])
    
    def _cb(self, change):
        self.change = change['owner']
        self.data = change['owner'].data
        self.filename = change['owner'].filename
        self.file_HTML.value = self.filename



class DownloadFile:
    
    def __init__(self, db_com, event_id, folder = './tmp_download/'):
        
        self.db_com = db_com
        self.folder = folder
        self.event_id = event_id

        self.delete_old_files() # deletes files in folder which are older than a day
        
        self.widget = self.create_download_link()
        

    def delete_old_files(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(1)
        for one_file in os.listdir(self.folder):
            file_path = os.path.join(self.folder, one_file)
            created_on = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
            
            if os.path.isfile(file_path) and created_on < yesterday:
                os.remove(file_path)
        
        
    def create_download_link(self): 
    
        if self.event_id is None:
            return None
        
        session = self.db_com.session()
    
        event_with_attachment = session.query(vb.db.Sample_Event).filter_by(id=self.event_id).first()
        attachment = event_with_attachment.attachment
        if attachment is None:
            return None
        
        filename = attachment.filename
        new_file = self.folder + filename
    
        output_file = open(new_file,'wb')
        output_file.write(attachment.data)
        output_file.close()
        
        return FileLink(new_file)
        


##############################################################
################### INPUT CLASSES ############################
##############################################################
        
class User_Input(Data_Input):

    def __init__(self, db_com):
        
        super().__init__(db_com)
        self.name_wText  = widgets.Text(value='Max Mustermann',description='Name:')
        self.alias_wText = widgets.Text(value='',description='Alias:')
        self.email_wText = widgets.Text(value='',description='E-Mail:')
        self.phone_wText = widgets.Text(value='',description='Phone:')

        items = [self.name_wText,
                 self.alias_wText,
                 self.email_wText,
                 self.phone_wText,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    
    def data_submission(self):
        session = self.db_com.session()
        
        user = db.User(
                username      = self.name_wText.value,
                alias         = self.alias_wText.value,
                email         = self.email_wText.value,
                phone         = self.phone_wText.value,
                )
        
        session.add(user)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'User added'
        return notifier_message
    
    def update_lists(self):
        pass
    

class Maskset_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.user_selector = User_Selector(self.db_com)

        self.name_wText         = widgets.Text(value='A12',description='Name:')
        self.comment_wTextarea  = widgets.Textarea(value='',description='Comment',disabled=False)

        items = [self.user_selector.widget,
                 self.name_wText,
                 self.comment_wTextarea,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    
    def data_submission(self):
        session = self.db_com.session()
        
        name = self.name_wText.value
        sample = db.Sample(
                user            = self.user_selector.wDropdown.value,
                samplename      = name,
                sample_types    = 'mask set',
                comment         = self.comment_wTextarea.value,
                session         = session
                )
        
        session.add(sample)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'Mask set "' + name + '" added'
        return notifier_message
    
    def update_lists(self):
        pass

class Wafer_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.user_selector = User_Selector(self.db_com)

        self.maskset_selector   = Sample_Selector(self.db_com, description = 'Mask Set', parent = '*', sample_type = 'mask set')
        
        self.name_wText         = widgets.Text(value='180131A',description='Name:')
        self.comment_wTextarea  = widgets.Textarea(value='',description='Comment',disabled=False)

        items = [self.user_selector.widget,
                 self.maskset_selector.widget,
                 self.name_wText,
                 self.comment_wTextarea,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    
    def data_submission(self):
        session = self.db_com.session()
        
        name = self.name_wText.value.upper()
        parent = self.maskset_selector.wDropdown.value
        sample_type = 'wafer'
        sample_type = vb.db_tools.get_sample_type(session, sample_type)
        
        if not re.match(sample_type.regular_expression, name): name = parent + '-' + name
        
        if not parent == name[0:len(parent)]: raise ValueError('Wafer name does not match name of mask set')
            
        sample = db.Sample(
                user            = self.user_selector.wDropdown.value,
                samplename      = name,
                sample_types    = sample_type,
                comment         = self.comment_wTextarea.value,
                parents         = parent,
                session         = session
                )
        
        session.add(sample)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'Wafer "' + name + '" added'
        return notifier_message
    
    def update_lists(self):
        self.maskset_selector.update_list()
    
    
class DIE_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.user_selector          = User_Selector(self.db_com)
        self.maskset_selector       = Sample_Selector(self.db_com, description = 'Mask Set', parent = '*', sample_type = 'mask set')
        
        init_maskset                = self.maskset_selector.wDropdown.value
        self.wafer_selector         = Sample_Selector(self.db_com, description = 'Mask Set', parent = init_maskset, sample_type = 'wafer')

        self.maskset_selector.wDropdown.observe(self.handle_maskset_change, names = 'value')
        
        self.sample_type_selector   = Sample_Type_Selector(self.db_com, multiple = False, remove_from_list = ['_default', 'mask set', 'wafer', 'die'])
        
        self.name_wText             = widgets.Text(value='AX987',description='Name:')
        self.comment_wTextarea      = widgets.Textarea(value='',description='Comment',disabled=False)

        items = [self.user_selector.widget,
                 self.maskset_selector.widget,
                 self.wafer_selector.widget,
                 self.name_wText,
                 self.sample_type_selector.widget,
                 self.comment_wTextarea,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    def handle_maskset_change(self, change):
        self.wafer_selector.parent = self.maskset_selector.wDropdown.value
        self.wafer_selector.update_list()
    
    def data_submission(self):
        
        session = self.db_com.session()
         
        
        name            = self.name_wText.value.upper()
        parent          = self.wafer_selector.wDropdown.value
        sample_types    = self.sample_type_selector.wDropdown.value
        
        if type(sample_types) is tuple: sample_types = list(sample_types)
        if type(sample_types) is not list: sample_types = [sample_types]
        sample_types.append('die')
        
        for sample_type in sample_types:
            sample_type = vb.db_tools.get_sample_type(session, sample_type)
            if not re.match(sample_type.regular_expression, name): name = parent + '-' + name
        
        if not parent == name[0:len(parent)]: raise ValueError('Sample name does not match name of wafer or regular expression of sample type')
      
        #sample_type = vb.db_tools.get_sample_type(session, sample_type)
        #if not re.match(sample_type.regular_expression, name): name = parent + name
        
        sample = db.Sample(
                user            = self.user_selector.wDropdown.value,
                samplename      = name,
                sample_types    = sample_type,
                comment         = self.comment_wTextarea.value,
                parents         = parent,
                session         = session
                )
        
        session.add(sample)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'Sample ' + name + ' added'
        return notifier_message

    def update_lists(self):
        self.maskset_selector.update_list()
        self.wafer_selector.update_list()
        self.user_selector.update_list()
        self.sample_type_selector.update_list()


class Sample_Type_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.name_wText         = widgets.Text(value='type name',description='Name:')
        self.regexp_wText       = widgets.Text(value='^[A-Z]{2}[0-9]{3}$',description='RegExp:')
        self.comment_wTextarea  = widgets.Textarea(value='e.g. two capital letters and three digits',description='Comment',disabled=False)

        items = [self.name_wText,
                 self.comment_wTextarea,
                 self.regexp_wText,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    
    def data_submission(self):
        session = self.db_com.session()
        sample_type = db.Sample_Type(
              typename              = self.name_wText.value,
              regular_expression    = self.letter_wText.value,
              comment               = self.comment_wTextarea.value
              )
        
        session.add(sample_type)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'Sample Type added'
        return notifier_message

    def update_lists(self):
        pass


class Sample_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.user_selector      = User_Selector(self.db_com)
        
        
        self.type_selector      = Sample_Type_Selector(self.db_com, multiple = True)
        self.type_regexp_wHTML  = widgets.HTML(value='')
        self.type_selector.wDropdown.observe(self.handle_type_change, names = 'value')
        self.type_HBox          = widgets.HBox([self.type_selector.widget,self.type_regexp_wHTML])
        

        self.state_selector     = Sample_State_Selector(self.db_com, multiple = True)

        self.name_wText         = widgets.Text(value='',description='Name:')
        self.comment_wTextarea  = widgets.Textarea(value='',description='Comment',disabled=False)

        self.parent_selector    = Sample_Selector_Filter(self.db_com,description = 'Parent:')
        self.add_parent_wButton = widgets.Button(description='Add parent',disabled=False,button_style='')
        self.add_parent_wButton.on_click(self.add_parent_clicked)
        
        self.parent_HBox = widgets.HBox([self.parent_selector.widget, self.add_parent_wButton])
        
        self.parents_wText      = widgets.Text(value='',description='Parents:')

        
        
        items = [self.user_selector.widget,
                 self.name_wText,
                 self.parent_HBox,
                 self.parents_wText,
                 self.comment_wTextarea,
                 self.type_HBox,
                 self.state_selector.widget,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    def add_parent_clicked(self, b):
        
        new_parent = self.parent_selector.wDropdown.value
        self.parents_wText.value = self.parents_wText.value + new_parent + ','
            
    def data_submission(self):
        session = self.db_com.session()
        
        name    = self.name_wText.value
        name    = name.upper()
        
        parents = self.parents_wText.value
        parents = parents.replace(' ', '')
        parents = parents.strip(',')
        
        if parents == '':
            parents = None
        else:
            parents = parents.split(',')
            
        sample = db.Sample(
                user            = self.user_selector.wDropdown.value,
                samplename      = name,
                comment         = self.comment_wTextarea.value,
                sample_types    = list(self.type_selector.wDropdown.value),
                sample_states   = list(self.state_selector.wDropdown.value),
                parents         = parents,
                session         = session
                )
        
        session.add(sample)
        self.db_com.commit_and_close(session)
        
        notifier_message = 'Sample "' + name + '" added'
        return notifier_message
    
    def handle_type_change(self, change):
        session     = self.db_com.session()
        type_list   = self.type_selector.wDropdown.value
        regexp_str  = '<font color="blue"> Regular Expressions:</font><br/>'
        
        for type_name in type_list:
            type_obj    = vb.db_tools.get_sample_type(session, type_name)
            regexp      = type_obj.regular_expression
            regexp_str  = regexp_str + '<font color="blue"><i>' + regexp + '</i></font><br/>'
        
        self.type_regexp_wHTML.value = regexp_str
        
        self.db_com.commit_and_close(session)
    
    def update_lists(self):
        self.user_selector.update_list()
        self.state_selector.update_list()
        self.type_selector.update_list()
        self.parent_selector.update_list()
    
    
class Sample_Event_Input(Data_Input):

    def __init__(self, db_com):
        super().__init__(db_com)
        
        self.user_selector      = User_Selector(self.db_com)
        self.sample_selector    = Sample_Selector_Filter(self.db_com)
        self.type_selector      = Sample_Event_Type_Selector(self.db_com)
        self.upload_file        = BrowseFile()
        
        self.name_wText         = widgets.Text(value='',description='Name:')
        self.comment_wTextarea  = widgets.Textarea(value='',description='Comment',disabled=False)
        
        items = [self.user_selector.widget,
                 self.sample_selector.widget,
                 self.type_selector.widget,
                 self.comment_wTextarea,
                 self.upload_file.widget,
                 self.submit_wButton,
                 self.notify_wHTML]
        
        self.widget = widgets.VBox(items)
        
    
    def data_submission(self):
        session = self.db_com.session()
        emptiness = [None, '']
        if self.upload_file.file_HTML.value not in emptiness:
            attachment = db.Attachment(self.upload_file.data, self.upload_file.filename)
        else:
            attachment = None
            
        timestamp = datetime.datetime.now()
        sample_event = db.Sample_Event(
                user                = self.user_selector.wDropdown.value,
                sample              = self.sample_selector.wDropdown.value,
                sample_event_type   = self.type_selector.wDropdown.value,
                timestamp           = timestamp,
                comment             = self.comment_wTextarea.value,
                attachment          = attachment,
                session             = session
                )
        
        session.add(sample_event)
        self.db_com.commit_and_close(session)
        
        self.upload_file.file_HTML.value = ''
        
        notifier_message = 'Sample Event added (' + timestamp.strftime('%H:%M:%S') + ')'
        return notifier_message
    
    def update_lists(self):
        self.user_selector.update_list()
        self.sample_selector.update_list()
        self.type_selector.update_list()
    
    
##############################################################
###################### BIG WIDGET ############################
##############################################################

class DB_Entries:
    
    def __init__(self):
        
        self.db_com = vb.db.DB_COM(vb.db.DBinfo)
        
        self.sample_input       = Sample_Input(self.db_com)
        self.sample_event_input = Sample_Event_Input(self.db_com)
        self.sample_type_input  = Sample_Type_Input(self.db_com)
        self.user_input         = User_Input(self.db_com)

#        self.maskset_input      = Maskset_Input(self.db_com)
#        self.wafer_input        = Wafer_Input(self.db_com)
#        self.die_input          = DIE_Input(self.db_com)

        self.accordion_children = [self.sample_input,
                                   self.sample_event_input,
                                   self.sample_type_input,
                                   self.user_input]
        
        # update all lists in case anything has been added
        
        
        # observer list for all submit buttons
        self.submit_observer = []
        for child in self.accordion_children:    
            self.submit_observer.append(child.submit_wButton.on_click(self.handle_input_change))
    
        self.children_widgets    = [child.widget for child in self.accordion_children]
        self.accordion           = widgets.Accordion(children = self.children_widgets)
            
        self.accordion.set_title(0, 'New Sample')
        self.accordion.set_title(1, 'New Sample Event')
        self.accordion.set_title(2, 'New Sample Type')
        self.accordion.set_title(3, 'New User')

#        self.accordion.set_title(3, 'New Mask Set')
#        self.accordion.set_title(4, 'New Wafer')
#        self.accordion.set_title(5, 'New DIE')
        
        
        self.widget = self.accordion
        
        display(self.widget)

    def handle_input_change(self, change):
            for child in self.accordion_children:
                child.update_lists()

class Sample_Selection:
    
    def __init__(self, db_com, multiple = False, allow_all = False, orientation = 'V'):
        
        
        self.db_com             = db_com
        self.multiple           = multiple
        self.orientation        = orientation
        self.allow_all          = allow_all

        self.maskset_selector   = Sample_Selector(self.db_com,
                                                  description   = 'Mask Set',
                                                  parent        = '*',
                                                  allow_all     = self.allow_all,
                                                  sample_type   = 'mask set')
        
        init_maskset            = self.maskset_selector.wDropdown.value
        self.wafer_selector     = Sample_Selector(self.db_com,
                                                  description   = 'Wafer',
                                                  parent        = init_maskset,
                                                  allow_all     = self.allow_all,
                                                  sample_type   = 'wafer')
        
        init_wafer              = self.wafer_selector.wDropdown.value
        self.sample_selector    = Sample_Selector(self.db_com,
                                                  parent        = [init_maskset, init_wafer],
                                                  sample_type   = 'die',
                                                  multiple      = self.multiple)
    
        self.maskset_selector.wDropdown.observe(self.handle_maskset_change, names = 'value')
        self.wafer_selector.wDropdown.observe(self.handle_wafer_change, names = 'value')
        #self.sample_selector.wDropdown.observe(self.handle_sample_change, names = 'value')
    
        if orientation == 'V':
            self.widget = widgets.VBox([self.maskset_selector.widget,self.wafer_selector.widget,self.sample_selector.widget])
        elif orientation == 'H':
            self.widget = widgets.HBox([self.maskset_selector.widget,self.wafer_selector.widget,self.sample_selector.widget])


    def handle_maskset_change(self, change):
        self.wafer_selector.parent = self.maskset_selector.wDropdown.value
        #self.design_selector.update_list()
        self.wafer_selector.update_list()
        
    def handle_wafer_change(self, change):
        self.sample_selector.parent = self.wafer_selector.wDropdown.value
        self.sample_selector.update_list()
        
    def handle_sample_change(self, change):
        self.sample_selector.wDropdown.value = self.sample_selector.wDropdown.value
        self.sample_selector.update_list()



        
class Plot_SMU_Data:
    
    def __init__(self):
        
        self.db_com = vb.db.DB_COM(vb.db.DBinfo)
        
#        self.sample_selection = Sample_Selection(self.db_com, allow_all = True, orientation = 'H')
#
#        self.sample_selection.sample_selector.wDropdown.observe(self.handle_selection_change, names = 'value')
        
        self.sample_selector    = Sample_Selector_Filter(self.db_com)
        self.sample_selector.wDropdown.observe(self.handle_selection_change, names = 'value')
        
        self.table_wOutput = widgets.Output()
       
        self.plot_wButton = widgets.Button(description='Plot',disabled=False,button_style='')
        self.plot_wButton.on_click(self.plot_clicked)
        
        self.bias_time = widgets.Checkbox(value=False,description='Bias Time', disabled=False)
        
        self.remove_wButton = widgets.Button(description='Remove',disabled=False,button_style='')
        self.remove_wButton.on_click(self.remove_clicked)

        self.notify_wHTML   = widgets.HTML(value='')

        self.samples_to_plot = {}
        #self.meas_data = {}
        self.plotlist_wSelectMultiple = widgets.SelectMultiple(
                options= [],
                description = 'Data:',
                layout=widgets.Layout(width='50%', height='100px'))


        self.plot_wOutput = widgets.Output()
        
        self.widget = widgets.VBox([
                self.sample_selector.widget,
                self.table_wOutput,
                self.plotlist_wSelectMultiple,
                widgets.HBox([self.plot_wButton,self.bias_time, self.remove_wButton]),
                self.plot_wOutput,
                self.notify_wHTML])
        self.handle_selection_change('NEW')
     
        display(self.widget)

        
    def set_notify(self, message, color):
        message = '<font color="' + color + '">' + str(message) + ' </font>'
        self.notify_wHTML.value = message
        
        
    def plot_clicked(self, b):
        meas_data = {}
        for key in self.plotlist_wSelectMultiple.options:
            #if key not in list(meas_data.keys()):
            measurement_series_id = self.samples_to_plot[key]['measurement_series_id']
            session = self.db_com.session()
            
            query = session.query(db.Sample_Event.timestamp,db.SMU_Measurement)\
                .join(db.SMU_Measurement.sample_event)\
                .join(db.SMU_Measurement.measurement_series)\
                .filter_by(id=measurement_series_id)
            meas_data[key] = pd.read_sql(query.statement, query.session.bind)

        try: self.plot_data(meas_data)
        except Exception as e: self.set_notify(e, 'red')
        
        
    def remove_clicked(self, b):
        
        for key in self.plotlist_wSelectMultiple.value:
            try: self.samples_to_plot.pop(key)
            except Exception as e: self.set_notify(e, 'red')
        self.plotlist_wSelectMultiple.options = list(self.samples_to_plot.keys())
        
    
    def plot_data(self,meas_data):
        plot_data = []            
        for key in list(meas_data.keys()):
            df = meas_data[key]
            if self.bias_time.value is True:
                df['timestamp'] = pd.to_datetime((df['timestamp'] - df['timestamp'][0]).astype('timedelta64[s]'), unit='s')
            plot_data.append(go.Scatter(
                    x = df['timestamp'],
                    y = df['resistance_mean'],
                    name = self.samples_to_plot[key]['sample_name']))
            
        self.plot_wOutput.clear_output(wait=True)
        with self.plot_wOutput:
            cf.go_offline() # required to use plotly offline (no account required).
            py.init_notebook_mode() # graphs charts inline (IPython).
            
            try:
                if self.bias_time.value is True:
                    layout = go.Layout(xaxis={
                        'type': 'time',
                        'tickformat': '%d:%H:%M:%S'
                        })
                
                    fig = go.Figure(data=plot_data, layout=layout)
                else:
                    fig = go.Figure(data=plot_data)
                py_plot = py.iplot(fig)
                display(py_plot)
            except Exception as e:
                self.set_notify(e, 'red')
                return

            
        
        
    def handle_selection_change(self, change):
        sample = self.sample_selector.wDropdown.value
        
        if sample is None: pass
        elif type(sample) is str:
            try: self.update_table(sample)
            except Exception as e: self.set_notify(e, 'red')
        else: return
    
    def update_table(self, sample):
    
        session = self.db_com.session()
        
        sample = vb.db_tools.get_sample(session, sample) 
        query = session.query(db.Sample_Event_Type.eventtypename, db.Sample_Event)\
            .filter_by(frequent_event = False)\
            .join(db.Sample_Event_Type.sample_events)\
            .filter_by(sample_id=sample.id)\
            .filter_by(state_active=True)
                    
        self.df = pd.read_sql(query.statement, query.session.bind)
        
#        remove_columns = ['sample_event_type_id','user_id', 'sample_id', 'state_active', 'prev_id']
#        self.df = self.df.drop(remove_columns, axis='columns')

        cols = ['id', 'timestamp', 'eventtypename', 'comment', 'attachment_id']
        self.df = self.df[cols]
        self.table_wOutput.clear_output(wait=True)
        
        with self.table_wOutput:
            table = bx.TableDisplay(self.df)

            table.setDoubleClickAction(lambda row, column, tabledispaly: self.add_to_plot_list(
                    sample.samplename,
                    tabledispaly.values[row][self.df.columns.get_loc('id')],
                    tabledispaly.values[row][self.df.columns.get_loc('eventtypename')]))

            display(table)
            
        session.close()
        
    def add_to_plot_list(self, sample_name, sample_event_id, sample_event_type):
        if sample_event_type != 'measurement_series':
            self.set_notify('Selected column is not a measurement series', 'red')
            return
        
        session = self.db_com.session()
        series_event = session.query(db.Sample_Event, db.Measurement_Series)\
            .filter_by(id = sample_event_id)\
            .join(db.Sample_Event.measurement_series).first()
        
        if series_event.Measurement_Series.measurement_type.meastypename != 'resistance':
            self.set_notify('Selected column is not a resistance measurement', 'red')
            return
        
        series_tag = sample_name + ' (SeriesID=' + str(sample_event_id) + ')'
        
        if series_tag in list(self.samples_to_plot.keys()):
            self.set_notify('Series already in the list, doing nothing', 'red')
            return
        
        self.samples_to_plot[series_tag] = {
                'sample_name':              sample_name,
                'sample_event_id':          sample_event_id,
                'measurement_series_id':    series_event.Measurement_Series.id}
        
        self.set_notify(series_tag + ' added', 'green')
        
        self.plotlist_wSelectMultiple.options = list(self.samples_to_plot.keys())
        
        
        
                
        
class Browse_Sample_Events:
    
    def __init__(self):
        
        self.db_com = vb.db.DB_COM(vb.db.DBinfo)
        
        # select sample from dropdown, on selection -> draw table with event list
        self.sample_selector    = Sample_Selector_Filter(self.db_com)
        self.sample_selector.wDropdown.observe(self.handle_selection_change, names = 'value')
        
        self.new_event_wButton  = widgets.Button(description='New Event',disabled=False,button_style='')
        self.new_event_wButton.on_click(self.new_event_clicked)
        
        self.firstline_wHBox    = widgets.HBox([self.sample_selector.widget,
                                                self.new_event_wButton])
        
        self.sample_event_input = Sample_Event_Input(self.db_com)
        self.sample_event_input.submit_wButton.on_click(self.handle_selection_change)
        
        self.table_wOutput = widgets.Output()
        self.event_wOutput = widgets.Output()
        
        self.notify_wHTML   = widgets.HTML(value='')
        
        
        self.widget = widgets.VBox([
                self.firstline_wHBox,                
                self.table_wOutput,
                self.event_wOutput,
                self.notify_wHTML])
    
        display(self.widget)
     
        
    def set_notify(self, message, color):
        message = '<font color="' + color + '">' + str(message) + ' </font>'
        self.notify_wHTML.value = message
        
    def display_on_event_output(self, widget):
        self.event_wOutput.clear_output(wait=True)
        with self.event_wOutput:
            display(widget)   
            
    def new_event_clicked(self, b):
        self.sample_event_input.sample_selector.filter_wText.value = self.sample_selector.wDropdown.value
        self.display_on_event_output(self.sample_event_input.widget)
        
    def handle_selection_change(self, change):
        sample = self.sample_selector.wDropdown.value
        if type(sample) is str:
            try: self.update_table(sample)
            except Exception as e: self.set_notify(e, 'red')
        else: return
    
    
    def update_table(self, sample):
    
        session = self.db_com.session()
        
        sample = vb.db_tools.get_sample(session, sample) 
            
        query = session.query(db.Sample_Event_Type.eventtypename,db.Sample_Event)\
            .filter_by(frequent_event = False)\
            .join(db.Sample_Event_Type.sample_events)\
            .filter_by(sample_id=sample.id)\
            .filter_by(state_active=True)\
            .outerjoin(db.Measurement_Series)\
            .outerjoin(db.Measurement_Type)\
            .add_column(db.Measurement_Type.meastypename)\
            .outerjoin(vb.db.User)\
            .add_column(vb.db.User.username)\
            .outerjoin(vb.db.Attachment)\
            .add_column(vb.db.Attachment.filename)
            
        self.df = pd.read_sql(query.statement, query.session.bind)
        
        
        cols = ['id', 'timestamp', 'username', 'eventtypename', 'meastypename', 'comment', 'filename']
        self.df = self.df[cols]
        
        self.df = self.df.rename(columns={'timestamp':      'Time',
                                          'username':       'User',
                                          'eventtypename':  'Event Type',
                                          'meastypename':   'Measurement Type',
                                          'comment':        'Comment',
                                          'filename':       'Attachment'})
        
        self.df.sort_values('Time')    
        
        self.table_wOutput.clear_output(wait=True)
        
        with self.table_wOutput:
            table = bx.TableDisplay(self.df)

            table.setDoubleClickAction(lambda row, column, tabledispaly: self.event_clicked(
                    sample.samplename,
                    tabledispaly.values[row][self.df.columns.get_loc('id')],
                    tabledispaly.values[row][self.df.columns.get_loc('Event Type')],
                    tabledispaly.values[row][self.df.columns.get_loc('Measurement Type')],
                    cols[column]))

            display(table)
            
        session.close()
     
    def event_clicked(self,
                      sample_name,
                      sample_event_id,
                      sample_event_type,
                      measurement_type,
                      column_clicked):
        
        session = self.db_com.session()

        if column_clicked == 'Attachment':
            link = DownloadFile(self.db_com, sample_event_id)
            self.display_on_event_output(link.widget)
            return
        
        sample = vb.db_tools.get_sample(session, sample_name)
        event = session.query(db.Sample_Event).filter_by(id = sample_event_id).first()
                    
        samplename_wHTML    = widgets.HTML(value='Sample name: <b>' + sample_name + '</b>')
        samplecomment_wHTML = widgets.HTML(value='Sample comment:<br/><textarea rows="2" cols="50">' + sample.comment + '</textarea> <br/>')
        sample_side         = widgets.VBox([samplename_wHTML,samplecomment_wHTML])
        
        eventtype_wHTML     = widgets.HTML(value='Event type: <i>' + sample_event_type + '</i>')
        eventcomment_wHTML  = widgets.HTML(value='Event comment:<br/><textarea rows="2" cols="50">' + event.comment + '</textarea>')
        event_side          = widgets.VBox([eventtype_wHTML,eventcomment_wHTML])
        
        info_list           = [sample_side, event_side]
        info_page           = widgets.HBox(info_list)

        plot_wOutput = widgets.Output()
        event_page = widgets.VBox([info_page,plot_wOutput])
        self.display_on_event_output(event_page)
        
        #RESISTANCE MEASUREMENT
        if sample_event_type == 'measurement_series' and measurement_type == 'resistance':
            
            series_start = session.query(db.Sample_Event).filter_by(id=sample_event_id).outerjoin(db.Measurement_Series).first()

            measurement_series_id = series_start.measurement_series[0].id

            query = session.query(db.Sample_Event.timestamp,db.SMU_Measurement)\
                .join(db.SMU_Measurement.sample_event)\
                .join(db.SMU_Measurement.measurement_series)\
                .filter_by(id=measurement_series_id)
                
            df = pd.read_sql(query.statement, query.session.bind)
            plot_data = [go.Scatter(
                    x = df['timestamp'],
                    y = df['resistance_mean'],
                    error_y=dict(
                        type='data',
                        array=df['resistance_std'],
                        visible=True
                    ),
                    name = sample_name)]
            with plot_wOutput:
                cf.go_offline() # required to use plotly offline (no account required).
                py.init_notebook_mode() # graphs charts inline (IPython).
                
                fig = go.Figure(data=plot_data)
                py_plot = py.iplot(fig)
                display(py_plot)
        
        
        session.close()
