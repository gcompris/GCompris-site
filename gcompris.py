#!/usr/bin/python3
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import jinja2
import time
import datetime
from datetime import date
import re
import gettext
from email import utils
from importlib import reload

reload(sys)

today = date.today()

try:
    version = sys.argv[1]
except:
    print("Missing GCompris version")
    sys.exit(1)

try:
    locale = sys.argv[2]
except:
    print("Missing GCompris locale")
    sys.exit(1)

try:
    localelist = sys.argv[3]
except:
    print("Missing GCompris list of locales")
    sys.exit(1)

try:
    gcomprisdir = sys.argv[4]
except:
    print("Missing GCompris installation directory, export GCOMPRIS_DIR as env var")
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
    _ = t.gettext

def formatDate(date):
    return date[0:4] + '-' + date[4:6] + '-' + date[6:8]

#
# Parse the config.c file in GCompris source code to get
# the name of the given locale.
#
def getLocaleName(locale):
    result = locale
    locales = {
        'en_GB': 'UK English', 'en_US': 'American English',
        'bg': u'български', 'br': 'Brezhoneg',
        'be': u'Беларуская', 'ca': u'Català',
        'cs': u'Česká', 'da': 'Dansk',
        'de': 'Deutsch', 'el': u'Ελληνικά',
        'es': u'Español', 'et': 'Eesti',
        'eu': 'Euskara', 'fi': 'Suomi',
        'fr': u'Français', 'ga': 'Gaeilge',
        'gd': u'Gàidhlig', 'gl': 'Galego',
        'hi': u'हिन्दी', 'hu': 'Magyar',
        'id': 'Indonesia', 'it': 'Italiano',
        'ko': u'한국어',
        'lt': u'Lietuvių', 'lv': u'Latviešu',
        'ml': u'മലയാളം', 'nl': 'Nederlands',
        'nn': 'Norsk (nynorsk)', 'pl': 'Polski',
        'pt': u'Português', 'pt_BR': u'Português do Brasil',
        'ro': u'Română', 'ruU': u'Русский',
        'sk': u'Slovenský', 'sl': 'Slovenski',
        'sr': u'црногорски jeзик', 'sv': 'Svenska',
        'ta': u'தமிழ்', 'th': u'ไทย',
        'tr': u'Türk', 'uk': u'український',
        'zh_CN': u'中文（简体）', 'zh_TW': u'繁體中文'
    }

    if locale in locales:
        result = locales[locale]
    else: # take the first key that starts with locale
        for loc in locales:
            if loc.startswith(locale):
                result = locales[loc]
                continue
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
templateEnv.install_gettext_callables(t.gettext, t.ngettext, newstyle=True)

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
    "license_info": _("This software is a GNU Package and is released under the GNU General Public License"),
    "feed": []
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
    templateOneNews = templateEnv.get_template("news/" + filename)
    templateVars['newsDate'] = formatDate(filename)
    templateVars['fileName'] = filename
    templateVars["news"].append(templateOneNews.render(templateVars))

    # read file to get the title, not sure if it is doable using jinja
    lines = ""
    with open ("news/" + filename, 'rt') as in_file:
        for line in in_file:
            lines += line.rstrip('\n')
    rgx = re.compile('set title = \'(?P<name>[^{}]+)\'')
    variable_names = {match.group('name') for match in rgx.finditer(lines)}

    dateRFC822 = utils.formatdate(time.mktime(datetime.datetime.strptime(templateVars['newsDate'], "%Y-%m-%d").timetuple()))
    currentFeed = {"dateRFC822": dateRFC822, "date": templateVars['newsDate'], "title": next(iter(variable_names))}

    templateVars["feed"].append(currentFeed)

templateNews = templateEnv.get_template("template/news.html")
outputNewsText = templateNews.render(templateVars)

templateNewsAll = templateEnv.get_template("template/newsall.html")
outputNewsAllText = templateNewsAll.render(templateVars)

templateFeedAll = templateEnv.get_template("template/feed.xml")
outputFeedAllText = templateFeedAll.render(templateVars)

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
templateScreenshot = templateEnv.get_template("template/screenshot.html")
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

templateScreenshots = templateEnv.get_template("template/screenshots.html")
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

templateDonate = templateEnv.get_template("template/donate.html")
outputDonateText = templateDonate.render(templateVars)

templateDownloads = templateEnv.get_template("template/downloads.html")
outputDownloadsText = templateDownloads.render(templateVars)

templateIndex = templateEnv.get_template("template/index.html")
outputIndexText = templateIndex.render(templateVars)

with codecs.open('index' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputIndexText )

with codecs.open('news' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputNewsText )

with codecs.open('newsall' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputNewsAllText )

with codecs.open('screenshots' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputScreenshotsText )

with codecs.open('donate' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputDonateText )

with codecs.open('downloads' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputDownloadsText )

with codecs.open('feed' + suffix + '.xml', 'w', encoding='utf8') as f:
    f.write( outputFeedAllText )

template = templateEnv.get_template("template/download_macosx.html")
outputText = template.render(templateVars)
with codecs.open('download_macosx' + suffix + '.html', 'w', encoding='utf8') as f:
    f.write( outputText )

if suffix == '-en':
    template = templateEnv.get_template("template/404.html")
    outputText = template.render(templateVars)
    with codecs.open('404.html', 'w', encoding='utf8') as f:
        f.write(outputText)
