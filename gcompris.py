#!/usr/bin/python3
# -*- coding: utf-8 -*-

import codecs
import os
import sys
import jinja2
import time
import datetime
import re
import gettext
from email import utils
from importlib import reload

from ActivityInfo import ActivityInfo
from ApplicationInfo import ApplicationInfo
from PyQt5.QtCore import QCoreApplication, QUrl, QTranslator
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType, QQmlComponent, QQmlEngine

reload(sys)

today = datetime.date.today()

try:
    version = sys.argv[1]
except IndexError:
    print("Missing GCompris version")
    sys.exit(1)

try:
    locale = sys.argv[2]
except IndexError:
    print("Missing GCompris locale")
    sys.exit(1)

try:
    localelist = sys.argv[3]
except IndexError:
    print("Missing GCompris list of locales")
    sys.exit(1)

try:
    gcomprisdir = sys.argv[4]
except IndexError:
    print("Missing GCompris installation directory, export GCOMPRIS_DIR as env var")
    sys.exit(1)

# Create Qt application to load the activities information from ActivityInfo.qml
app = QCoreApplication(sys.argv)
translator = QTranslator()
translator.load(str("locale/"+locale+"/LC_MESSAGES/gcompris_qt.qm"))
app.installTranslator(translator)

# Load the proper locale catalog
_ = None
t = None
def setLocale(locale):
    global _
    global t
    t = gettext.translation('gcompris', 'locale', languages=[locale], fallback=True)
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
        'ca@valencia': u'Català (Valencian)',
        'cs': u'Česká', 'da': 'Dansk',
        'de': 'Deutsch', 'el': u'Ελληνικά',
        'es': u'Español', 'et': 'Eesti',
        'eu': 'Euskara', 'fi': 'Suomi',
        'fr': u'Français', 'ga': 'Gaeilge',
        'gd': u'Gàidhlig', 'gl': 'Galego',
        'he': u'עברית',
        'hi': u'हिन्दी', 'hu': 'Magyar',
        'id': 'Indonesia', 'it': 'Italiano',
        'ko': u'한국어',
        'lt': u'Lietuvių', 'lv': u'Latviešu',
        'mk': u'Македонски',
        'ml': u'മലയാളം', 'nl': 'Nederlands',
        'nn': 'Norsk (nynorsk)', 'pl': 'Polski',
        'pt': u'Português', 'pt_BR': u'Português do Brasil',
        'ro': u'Română', 'ruU': u'Русский',
        'sk': u'Slovenský', 'sl': 'Slovenski',
        'sq': u'Shqip',
        'sr': u'црногорски jeзик', 'sv': 'Svenska',
        'ta': u'தமிழ்', 'th': u'ไทย',
        'tr': u'Türk', 'uk': u'українська',
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

    # create qml engine to read the files
    engine = QQmlEngine()
    component = QQmlComponent(engine)
    qmlRegisterSingletonType(ApplicationInfo, "GCompris", 1, 0, "ApplicationInfo", ApplicationInfo.createSingleton);
    qmlRegisterType(ActivityInfo, "GCompris", 1, 0, "ActivityInfo");

    activity_dir = gcomprisdir + "/src/activities"
    for activity in os.listdir(activity_dir):
        # Skip unrelevant activities
        if activity == 'template' or \
           not os.path.isdir(activity_dir + "/" + activity):
            continue
        
        try:
            component.loadUrl(QUrl(activity_dir + "/" + activity + "/ActivityInfo.qml"))
            activityInfo = component.create()
            if activityInfo is None:
                # Print all errors that occurred.
                for error in component.errors():
                    print(error.toString())
                exit(-1)
            # ignore disabled activities
            if not activityInfo.property('enabled'):
                print("Disabling", activityInfo.property('name'))
                continue
            description = activityInfo.property('description').replace('\n', '<br/>')
            name = activityInfo.property('name').split('/')[0]
            title = activityInfo.property('title')
            credit = activityInfo.property('credit').replace('\n', '<br/>')
            goal = activityInfo.property('goal').replace('\n', '<br/>')
            section = activityInfo.property('section')
            author = activityInfo.property('author')
            if 'Timothée Giet' in author or author == "":
                author = re.sub("&lt;.*?&gt;", "", author)
            else:
                author = re.sub("&lt;.*?&gt;", "", author)+(' & Timothée Giet')

            manual = activityInfo.property('manual').replace('\n', '<br/>')
            difficulty = activityInfo.property('difficulty')
            category = activityInfo.property('category')
            prerequisite = activityInfo.property('prerequisite').replace('\n', '<br/>')
            if name != "menu":
                icon = activityInfo.property('icon').split('/')[1]

            infos = {'description':description, 
                     'name':name, 
                     'title':title, 
                     'credit':credit,
                     'goal':goal, 
                     'section':section,
                     'author':author,
                     'manual':manual,
                     'difficulty':difficulty,
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
templateEnv.install_gettext_callables(t.gettext, t.ngettext, newstyle=True, pgettext=t.pgettext)

# Specify any input variables to the template as a dictionary.
templateVars = {
    "locale" : locale,
    "direction" : "rtl" if locale == "he" else "ltr",
    "suffix" : suffix,
    "language" : language,
    "revision_date" : today.strftime("%Y-%m-%d"),
    "current_year": today.strftime("%Y"),
    "version": version,
    "news": [],
    "single_news": [],
    "screenshots": [],
    "screenshotsmenu": [],
    "locales": locales,
    "manual": getManual(),
    "license_info": _("This software is a GNU Package and is released under the GNU Affero General Public License."),
    "translators_names": t.pgettext("NAME OF TRANSLATORS", "Your names"),
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
for filename in os.listdir("newsTemplate"):
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
    templateOneNews = templateEnv.get_template("newsTemplate/" + filename)
    templateVars['newsDate'] = formatDate(filename)
    templateVars['fileName'] = filename
    templateVars["single_news"] = templateOneNews.render(templateVars)
    templateVars["news"].append(templateOneNews.render(templateVars))

    # read file to get the title, not sure if it is doable using jinja
    lines = ""
    with open ("newsTemplate/" + filename, 'rt') as in_file:
        for line in in_file:
            lines += line.rstrip('\n')
    rgx = re.compile('set title = [\'"](?P<name>[^{}]+)[\'"]')
    variable_names = {match.group('name') for match in rgx.finditer(lines)}

    dateRFC822 = utils.formatdate(time.mktime(datetime.datetime.strptime(templateVars['newsDate'], "%Y-%m-%d").timetuple()))
    currentFeed = {"dateRFC822": dateRFC822, "date": templateVars['newsDate'], "title": next(iter(variable_names))}

    templateVars["feed"].append(currentFeed)

    templateNewsSingle = templateEnv.get_template("template/singlenews.html")
    outputNewsSingleText = templateNewsSingle.render(templateVars)

    with codecs.open('news/' + templateVars['newsDate'] + suffix + '.html', 'w', encoding='utf8') as f:
        f.write( outputNewsSingleText )

#
# Get the board list and make some adaptations
#
boards = getBoards()

for screenshot in boards:
    if screenshot['name'] == 'menu':
        screenshot['name'] = 'root'
        screenshot['section'] = 'administration'
        screenshot['type'] = 'root menu'
        screenshot['difficulty'] = "0"

    if screenshot['name'] == "login":
        screenshot['section'] = 'administration'

boards = sorted(boards, key=lambda t: t['section']+' '+t['name'])

#
# Now process the board list
#
templateScreenshot = templateEnv.get_template("template/screenshot.html")
previousSection = ''
depth = 0

for screenshot in boards:
    if screenshot['section'] == '/experimental' or screenshot['name'] == 'experimental':
        continue

    templateVars["screenshot"] = screenshot
    screenshot["depth"] = depth
    templateVars["depth"] = depth
    templateVars["screenshots"].append(templateScreenshot.render(templateVars))

    # Create the screenshot menu
    templateVars["screenshotsmenu"].append(screenshot)

(opens, closes) = sectionDiff(previousSection, '')
templateVars["screenshots"].append("</div>" * closes)

# Count the number of activities
total_activities = 0
for screenshot in boards:
    if screenshot['name'] != 'root':
        total_activities += 1

templateVars['total_activities'] = total_activities

templateFeedAll = templateEnv.get_template("template/feed.xml")
outputFeedAllText = templateFeedAll.render(templateVars)

with codecs.open('feed' + suffix + '.xml', 'w', encoding='utf8') as f:
    f.write(outputFeedAllText)

for f in ["christmas", "schools", "donate", "downloads", "index", "screenshots", "news", "newsall"]:
    template = templateEnv.get_template(os.path.join("template/", f + ".html"))
    outputText = template.render(templateVars)
    with codecs.open(f + suffix + '.html', 'w', encoding='utf8') as output:
        output.write(outputText)

if suffix == '-en':
    template = templateEnv.get_template("template/404.html")
    outputText = template.render(templateVars)
    with codecs.open('404.html', 'w', encoding='utf8') as f:
        f.write(outputText)
