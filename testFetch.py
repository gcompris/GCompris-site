#!/usr/bin/python2
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import jinja2
from datetime import date
import sqlite3
import re
from collections import OrderedDict
import gettext
from os.path import expanduser

reload(sys)
sys.setdefaultencoding('utf-8')

today = date.today()
    

descriptions = []

    
def getBoards():
    '''create a list of activity infos as found in GCompris ActivityInfo.qml'''



    activity_dir = expanduser("~") +"/Softs/src/gcompris/src/activities"
    for activity in os.listdir(activity_dir):
        # Skip unrelevant activities
        if activity == 'template' or \
           activity == 'menu' or \
           not os.path.isdir(activity_dir + "/" + activity):
            continue
        
        try:
            with open(activity_dir + "/" + activity + "/ActivityInfo.qml") as f:
                content = f.readlines()
                
                description = ''
                name = ''
                title = ''
                credit = ''
                goal = ''
                section = ''
                author = ''
                manual = ''
                difficulty = ''
                demo = ''
 #              type = ''
                prerequisite = ''
                icon = ''

                for line in content:

                    m = re.match('.*description:.*\"(.*)\"', line)
                    if m:
                        description =  m.group(1)

                    m = re.match('.*name:.*\"(.*)\"', line)
                    if m:
                        name = m.group(1)
                    
                    m = re.match('.*title:.*\"(.*)\"', line)
                    if m:
                        infos = m.group(1)
                    
                    m = re.match('.*credit:.*\"(.*)\"', line)
                    if m:
                        credit = m.group(1)
                    
                    m = re.match('.*goal:.*\"(.*)\"', line)
                    if m:
                        goal = m.group(1)
                    
                    m = re.match('.*section:.*\"(.*)\"', line)
                    if m:
                        section = m.group(1)
                    
                    m = re.match('.*author:.*\"(.*)\"', line)
                    if m:
                        author = m.group(1)
                    
                    m = re.match('.*manual:.*\"(.*)\"', line)
                    if m:
                        manual = m.group(1)
                    
                    m = re.match('.*difficulty:.*\"(.*)\"', line)
                    if m:
                        difficulty = m.group(1)
                    
                    m = re.match('.*demo:.*\"(.*)\"', line)
                    if m:
                        demo = m.group(1)
                        
                    m = re.match('.*prerequisite:.*\"(.*)\"', line)
                    if m:
                        prerequisite = m.group(1)
                        
                        m = re.match('.*icon:.*\"(.*)\"', line)
                    if m:
                        icon = m.group(1)

                    
                    infos = {'description':description, 
                             'name':name, 
                             'title':title, 
                             'credit':credit,
                             'goal':goal, 
                             'section':section,
                             'author':author,
                             'manual':manual,
                             'difficulty':difficulty,
                             'demo':demo,
                             'prerequisite':prerequisite,
                             'icon':icon}
                
                descriptions.append(infos)    

        except IOError as e:
            pass
    
    return descriptions
     

boards = getBoards()
