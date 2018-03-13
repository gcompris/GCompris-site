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
import shutil



activity_dir = expanduser("~") +"/Softs/src/gcompris/src/activities"

for activity in os.listdir(activity_dir):
    # Skip unrelevant activities
    if activity == 'template' or \
        activity == 'menu' or \
        not os.path.isdir(activity_dir + "/" + activity):
        continue
        
    shutil.copy2(activity_dir + '/' + activity +'/' + activity + '.svg', '/home/timo/Softs/src/gcompris-net/boardicons/' + activity + '.svg')
        
print "Done"
