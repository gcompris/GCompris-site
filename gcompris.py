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

reload(sys)
sys.setdefaultencoding('utf-8')

today = date.today()

try:
    version = sys.argv[1]
except:
    print "Missing GCompris version"
    sys.exit(1)

try:
    locale = sys.argv[2]
except:
    print "Missing GCompris locale"
    sys.exit(1)

try:
    localelist = sys.argv[3]
except:
    print "Missing GCompris list of locales"
    sys.exit(1)

try:
    gcomprisdir = sys.argv[4]
except:
    print "Missing GCompris installation directory, export GCOMPRIS_DIR as env var"
    sys.exit(1)

# Load the proper locale catalog
_ = None
t = None
def setLocale(locale):
    global _
    global t
    try:
        t = gettext.translation('gcompris', 'locale', languages=[locale])
    except:
        t = gettext.NullTranslations()
    _ = t.ugettext

def formatDate(date):
    return date[0:4] + '-' + date[4:6] + '-' + date[6:8]

#
# Parse the config.c file in GCompris source code to get
# the name of the given locale.
#
def getLocaleName(locale):
    result = locale
    try:
        with open(gcomprisdir + '/src/core/LanguageList.qml') as f:
            content = f.readlines()
            for line in content:
                m = re.match('.*\"text\": \"(.*)\", \"locale\": \"(.*)\" }', line)
                if m and m.group(2).startswith(locale):
                    result = m.group(1)
                    break
    except IOError as e:
        pass

    return result

# Set the default locale
setLocale(locale)

#
# Create locales [ [ locale, language ], ...]
#
locales = []
language = ""
for loca in localelist.split():
    # We want each country in its own language
    setLocale(loca)
    lang = _(getLocaleName( loca ))
    locales.append( [loca, lang] )
    if locale == loca:
        language = lang

# Add en_US manually
setLocale("en")
locales.append( ['en', _(getLocaleName( 'en_US'))] )
if language == '':
    language = 'English'

# Back to the default locale
setLocale(locale)

locales = sorted(locales, key=lambda t: t[1])

suffix = '-' + locale

#
# We don't have a translation of each manual. If we have it
# we return it else we return the english one
def getManual():
    manuals = {
        'en': 'wiki/Manual',
        'fr': 'wiki/Manuel',
        'de': 'wiki/Benutzerhandbuch',
        'es': 'wiki/Manual_es',
        'pt_BR': 'wiki/Manual_pt-BR',
        'he': u'wiki/מדריך_למשתמש',
        'ru': u'wiki/Руководство'
        }
    if locale in manuals:
        return manuals[locale]
    return manuals['en']
    
    
    
descriptions = []

    
def getBoards():
    '''create a list of activity infos as found in GCompris ActivityInfo.qml'''

    activity_dir = gcomprisdir + "/src/activities"
    for activity in os.listdir(activity_dir):
        # Skip unrelevant activities
        if activity == 'template' or \
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
                category = ''
                prerequisite = ''
                icon = ''

                for line in content:

                    m = re.match('.*description:.*\"(.*)\"', line)
                    if m:
                        description =  m.group(1)

                    m = re.match('.*name:.*\"(.*)\"', line)
                    if m:
                        name = activity
                        icon = activity
                    
                    m = re.match('.*title:.*\"(.*)\"', line)
                    if m:
                        title = m.group(1)
                    
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
                        author = re.sub("&lt;.*?&gt;", "", m.group(1))+(' & Timothee Giet')
                    
                    m = re.match('.*manual:.*\"(.*)\"', line)
                    if m:
                        manual = m.group(1)
                    
                    m = re.match('.*difficulty:.*', line)
                    if m:
                        difficulty = (m.group(0)).replace('  difficulty: ', '')
                        difficulty = (difficulty).replace(' ', '')
                        
                    
                    m = re.match('.*demo:.*', line)
                    if m:
                        demo = (m.group(0)).replace('  demo: ', '')
                        
                    m = re.match('.*type:.*\"(.*)\"', line)
                    if m:
                        category = m.group(1)
                        
                    m = re.match('.*prerequisite:.*\"(.*)\"', line)
                    if m:
                        prerequisite = m.group(1)
                        

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
                             'type':category,
                             'prerequisite':prerequisite,
                             'icon':icon}
                
                descriptions.append(infos)    

        except IOError as e:
            pass
    
    return descriptions

# /a/b /a => 1 0
# /a/b /c => 2 1
# /a/b /a/b => 0 0
# /a '' =>  1 0
# /a/b/c/d /a/b/e/f => 2 2
# /a /a/b/c => 0 2
#
# Return (open, close)
#
def sectionDiff(old, new):
    if old == new:
        return (0, 0)

    olds = old.split("/")
    news = new.split("/")

    closes = 0
    opens = 0

    for i in range(0, max(len(olds), len(news)) ):
        try:
            if olds[i] == news[i]:
                continue
            else:
                closes += 1
                opens += 1
        except:
            if len(olds) > i:
                closes += 1
            else:
                opens += 1

    return (opens, closes)

templateLoader = jinja2.FileSystemLoader( searchpath="." )
templateEnv = jinja2.Environment( loader=templateLoader,
                                  extensions=['jinja2.ext.i18n'],
                                  trim_blocks=True,
                                  lstrip_blocks=True)
templateEnv.install_gettext_callables(t.ugettext, t.ungettext, newstyle=True)

# Specify any input variables to the template as a dictionary.
templateVars = {
    "locale" : locale,
    "suffix" : suffix,
    "language" : language,
    "vocabularyActivity" : _("Enrich your vocabulary"),
    "revision_date" : today.strftime("%Y-%m-%d"),
    "current_year": today.strftime("%Y"),
    "version": version,
    "news": [],
    "screenshots": [],
    "screenshotsmenu": [],
    "locales": locales,
    "manual": getManual(),
    "manualTranslation": _("Manual"),
    "license_info": _("This software is a GNU Package and is released under the GNU General Public License")
    }

# Use this filter in template when you know the text comes from the
# software part and should not be added to the web site po file.
def trans(text):
    return _(text)
templateEnv.filters['trans'] = trans

#
# Build a map of all news file to proceed for our locale
#
filenames = {}
for filename in os.listdir("news"):
    if not filename.endswith(".html"):
        continue

    # If a news is found with a -<LOCALE> suffix before .html
    # It supercede a news without a such suffix (english one).
    filename_noext = filename.split('.')[0]
    try:
        (dat, loc) = filename_noext.split('-')
        if locale == loc:
            filenames[dat] = filename
    except:
        if not filename_noext in filenames:
            filenames[filename_noext] = filename

for filename in sorted(filenames, reverse=True):
    filename = filenames[filename]
    templateOneNews = templateEnv.get_template( "news/" + filename )
    templateVars['newsDate'] = formatDate(filename)
    templateVars['fileName'] = filename
    templateVars["news"].append(templateOneNews.render( templateVars ))

templateNews = templateEnv.get_template( "template/news.html" )
outputNewsText = templateNews.render( templateVars )

templateNewsAll = templateEnv.get_template( "template/newsall.html" )
outputNewsAllText = templateNewsAll.render( templateVars )

#
# Get the board list and make some adaptations
#
boards = getBoards()
#print boards

for screenshot in boards:
    if screenshot['name'] == 'menu':
        screenshot['name'] = 'root'
        screenshot['section'] = 'administration'
        screenshot['type'] = 'root menu'
        screenshot['difficulty'] = "0"

    if screenshot['name'] == "login":
        screenshot['section'] = 'administration'

boards = sorted(boards, key=lambda t: t['section']+' '+t['name'])

# Reorder root, administration and login boards
#boards[0], boards[1], boards[2] = boards[2], boards[0], boards[1]

#
# Now process the board list
#
templateScreenshot = templateEnv.get_template( "template/screenshot.html" )
previousSection = ''
depth = 0

for screenshot in boards:
    if screenshot['section'] == '/experimental' or screenshot['name'] == 'experimental':
        continue

    #section = screenshot['section']
    #if screenshot['type'] == 'root menu':
        #section += "/" + screenshot['name']

    #(opens, closes) = sectionDiff(previousSection, section)
    #depth += opens - closes
    #if closes:
        #templateVars["screenshots"].append("</div>" * closes)
    #if opens:
        #templateVars["screenshots"].append("<div class='row screenshot" + str(depth) + "'>" * opens)

    #previousSection = section


    #screenshot['author'] = re.sub(r" \(.*\)", "", screenshot['author'])
    if screenshot['goal']:
        screenshot['goal'] = _(screenshot['goal']).replace('\n', '<br/>')
    if screenshot['prerequisite']:
        screenshot['prerequisite'] = _(screenshot['prerequisite']).replace('\n', '<br/>')
    if screenshot['manual']:
        screenshot['manual'] = _(screenshot['manual']).replace('\n', '<br/>')
    if screenshot['credit']:
        screenshot['credit'] = _(screenshot['credit']).replace('\n', '<br/>')
    if screenshot['title']:
        screenshot['title'] = _(screenshot['title'])
    if screenshot['description'] and screenshot['description'] != "":
        screenshot['description'] = _(screenshot['description'])
    templateVars["screenshot"] = screenshot
    screenshot["depth"] = depth
    templateVars["depth"] = depth
    templateVars["screenshots"].append(templateScreenshot.render( templateVars ))

    # Create the screenshot menu
    templateVars["screenshotsmenu"].append(screenshot)

(opens, closes) = sectionDiff(previousSection, '')
templateVars["screenshots"].append("</div>" * closes)

templateScreenshots = templateEnv.get_template( "template/screenshots.html" )
outputScreenshotsText = templateScreenshots.render( templateVars )

# Count the number of activities
demo_activities = 0
total_activities = 0
for screenshot in boards:
    if screenshot['name'] != 'root':
        total_activities += 1
        if screenshot['demo'] == "true":
            demo_activities += 1

templateVars['total_activities'] = total_activities
templateVars['demo_activities'] = demo_activities

templateBuy = templateEnv.get_template( "template/buy.html" )
outputBuyText = templateBuy.render( templateVars )

templateIndex = templateEnv.get_template( "template/index.html" )
outputIndexText = templateIndex.render( templateVars )

with codecs.open('index' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputIndexText )

with codecs.open('news' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputNewsText )

with codecs.open('newsall' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputNewsAllText )

with codecs.open('screenshots' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputScreenshotsText )

with codecs.open('buy' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputBuyText )

template = templateEnv.get_template( "template/download_macosx.html" )
outputText = template.render( templateVars )
with codecs.open('download_macosx' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputText )

if suffix == '-en':
    template = templateEnv.get_template( "template/404.html" )
    outputText = template.render( templateVars )
    with codecs.open('404.html', 'w', encoding='utf8') as f:
        f.write( outputText )
