#!/usr/bin/python
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

# Load the proper locale catalog
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
    with open("/home/bcoudoin/Projets/gcompris/src/gcompris/config.c", 'r') as f:
        inlist = False
        for line in f:
            line = line.rstrip()
            if line.startswith("static gchar *linguas[]"):
                inlist = True
                continue

            if line == "};":
                break

            if not inlist:
                continue

            sline = line.split(',')
            if sline[0].strip(' "').startswith(locale):
                result = sline[1].strip().replace('N_("', '').replace('")', '')
                break

    return result

#
# Create locales [ [ locale, language ], ...]
#
locales = []
language = ""
# for filename in os.listdir("/home/bcoudoin/Projets/gcompris/po"):
#     if filename.endswith('.po'):
#         loca = filename.replace('.po', '')
#         lang = _(getLocaleName( loca ))
#         locales.append( ['-' + loca, lang] )
#         if locale == loca:
#             language = lang
for loca in localelist.split():
    lang = _(getLocaleName( loca ))
    locales.append( ['-' + loca, lang] )
    if locale == loca:
        language = lang

# Add en_US manually
locales.append( ['-en', _(getLocaleName( 'en_US'))] )
if language == '':
    language = 'English'

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

def getBoards():
    con = sqlite3.connect("/home/bcoudoin/.config/gcompris/gcompris_sqlite.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('select name, section, author, difficulty, icon, title, description, prerequisite, goal, manual, credit, demo, type from boards order by section||\'/\'||name, difficulty')
    # Make a dict rw of the result
    return [dict(row) for row in cur]

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
                                  extensions=['jinja2.ext.i18n'] )
templateEnv.install_gettext_callables(t.ugettext, t.ungettext, newstyle=True)

# Specify any input variables to the template as a dictionary.
templateVars = {
    "locale" : locale,
    "suffix" : suffix,
    "language" : language,
    "title" : "GCompris Free Educational Software",
    "revision_date" : today.strftime("%Y-%m-%d"),
    "current_year": today.strftime("%Y"),
    "version": version,
    "news": [],
    "screenshots": [],
    "screenshotsmenu": [],
    "locales": locales,
    "manual": getManual(),
    "license_info": _("This software is a GNU Package and is released under the GNU General Public License")
    }

filenames = []
for filename in os.listdir("news"):
    if not filename.endswith(".html"):
        continue
    filenames.append(filename)

for filename in sorted(filenames, reverse=True):
    templateOneNews = templateEnv.get_template( "news/" + filename )
    templateVars['newsDate'] = formatDate(filename)
    templateVars["news"].append(templateOneNews.render( templateVars ))

templateNews = templateEnv.get_template( "template/news.html" )
outputNewsText = templateNews.render( templateVars )

templateNewsAll = templateEnv.get_template( "template/newsall.html" )
outputNewsAllText = templateNewsAll.render( templateVars )

#
# Get the board list and make some adaptations
#
boards = getBoards()
for screenshot in boards:
    if screenshot['name'] == "":
        screenshot['name'] = 'root'
        screenshot['section'] = '/administration'
        screenshot['type'] = 'root menu'

    if screenshot['name'] == "login":
        screenshot['section'] = '/administration'

boards = sorted(boards, key=lambda t: t['section']+'/'+t['name'])

# Reorder root, administration and login boards
boards[0], boards[1], boards[2] = boards[2], boards[0], boards[1]

#
# Now process the board list
#
templateScreenshot = templateEnv.get_template( "template/screenshot.html" )
previousSection = ''
depth = 0

for screenshot in boards:
    if screenshot['section'] == '/experimental' or screenshot['name'] == 'experimental':
        continue

    section = screenshot['section']
    if screenshot['type'] == 'menu':
        section += "/" + screenshot['name']

    (opens, closes) = sectionDiff(previousSection, section)
    depth += opens - closes
    if closes:
        templateVars["screenshots"].append("</div>" * closes)
    if opens:
        templateVars["screenshots"].append("<div class='row screenshot" + str(depth) + "'>" * opens)

    previousSection = section

    screenshot['icon'] = screenshot['icon'].replace(".svg", "")
    screenshot['icon'] = screenshot['icon'].replace(".png", "")
    screenshot['author'] = re.sub(r" \(.*\)", "", screenshot['author'])
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
    if screenshot['description']:
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
    if screenshot['type'] != 'menu':
        total_activities += 1
        if screenshot['demo'] == 1:
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

if suffix == '-en':
    template = templateEnv.get_template( "template/download_macosx.html" )
    outputText = template.render( templateVars )
    with codecs.open('download_macosx.html', 'w', encoding='utf8') as f:
        f.write( outputText )

    template = templateEnv.get_template( "template/404.html" )
    outputText = template.render( templateVars )
    with codecs.open('404.html', 'w', encoding='utf8') as f:
        f.write( outputText )
