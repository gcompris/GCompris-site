#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# GCompris - gcompris.py
#
# SPDX-FileCopyrightText: 2013 Bruno Coudoin <bruno.coudoin@gcompris.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import codecs
import os
import sys
import time
import datetime
import re
import gettext
from email import utils
from importlib import reload
import html

import htmlmin

from ActivityInfo import ActivityInfo
from ApplicationInfo import ApplicationInfo
from PyQt5.QtCore import QCoreApplication, QUrl, QTranslator
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType, QQmlComponent, QQmlEngine

import jinja2

from bs4 import BeautifulSoup

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
translator.load(str("po/"+locale+"/LC_MESSAGES/gcompris_qt.qm"))
app.installTranslator(translator)

# Load the proper locale catalog
_ = None
t = None
def setLocale(locale):
    global _
    global t
    t = gettext.translation('gcompris', 'po', languages=[locale], fallback=True)
    _ = t.gettext

def formatDate(date):
    return date[0:4] + '-' + date[4:6] + '-' + date[6:8]

#
# Parse the config.c file in GCompris source code to get
# the name of the given locale.
#
def getLocaleName(locale):
    result = locale

    if locale in gcomprisLocales:
        result = gcomprisLocales[locale]["original"]
    else: # take the first key that starts with locale
        for loc in gcomprisLocales:
            if loc["original"].startswith(locale):
                result = gcomprisLocales[loc]["original"]
                continue
    return result

# Set the default locale
setLocale(locale)

gcomprisLocales = {
    "en_GB": {"original": "UK English", "translated": t.pgettext("language name, item list", "UK English")},
    "en_US": {"original": "American English", "translated": t.pgettext("language name, item list", "American English")},
    "az": {"original": "Azərbaycanca", "translated": t.pgettext("language name, item list", "Azerbaijani")},
    "bg": {"original": "български", "translated": t.pgettext("language name, item list", "Bulgarian")},
    "br": {"original": "Brezhoneg", "translated": t.pgettext("language name, item list", "Breton")},
    "be": {"original": "Беларуская", "translated": t.pgettext("language name, item list", "Belarusian")},
    "ca": {"original": "Català", "translated": t.pgettext("language name, item list", "Catalan")},
    "ca@valencia": {"original": "Català (Valencian)", "translated": t.pgettext("language name, item list", "Catalan (Valencian)")},
    "cs": {"original": "Česká", "translated": t.pgettext("language name, item list", "Czech")},
    "da": {"original": "Dansk", "translated": t.pgettext("language name, item list", "Danish")},
    "de": {"original": "Deutsch", "translated": t.pgettext("language name, item list", "German")},
    "el": {"original": "Ελληνικά", "translated": t.pgettext("language name, item list", "Greek")},
    "es": {"original": "Español", "translated": t.pgettext("language name, item list", "Spanish")},
    "et": {"original": "Eesti", "translated": t.pgettext("language name, item list", "Estonian")},
    "eu": {"original": "Euskara", "translated": t.pgettext("language name, item list", "Basque")},
    "fi": {"original": "Suomi", "translated": t.pgettext("language name, item list", "Finnish")},
    "fr": {"original": "Français", "translated": t.pgettext("language name, item list", "French")},
    "ga": {"original": "Gaeilge", "translated": t.pgettext("language name, item list", "Irish")},
    "gd": {"original": "Gàidhlig", "translated": t.pgettext("language name, item list", "Scottish Gaelic")},
    "gl": {"original": "Galego", "translated": t.pgettext("language name, item list", "Galician")},
    "he": {"original": "עברית", "translated": t.pgettext("language name, item list", "Hebrew")},
    "hi": {"original": "हिन्दी", "translated": t.pgettext("language name, item list", "Hindi")},
    "hr": {"original": "Hrvatski", "translated": t.pgettext("language name, item list", "Croatian")},
    "hu": {"original": "Magyar", "translated": t.pgettext("language name, item list", "Hungarian")},
    "id": {"original": "Indonesia", "translated": t.pgettext("language name, item list", "Indonesian")},
    "it": {"original": "Italiano", "translated": t.pgettext("language name, item list", "Italian")},
    "ko": {"original": "한국어", "translated": t.pgettext("language name, item list", "Korean")},
    "lt": {"original": "Lietuvių", "translated": t.pgettext("language name, item list", "Lithuanian")},
    "lv": {"original": "Latviešu", "translated": t.pgettext("language name, item list", "Latvian")},
    "mk": {"original": "Македонски", "translated": t.pgettext("language name, item list", "Macedonian")},
    "ml": {"original": "മലയാളം", "translated": t.pgettext("language name, item list", "Malayalam")},
    "nl": {"original": "Nederlands", "translated": t.pgettext("language name, item list", "Dutch")},
    "nn": {"original": "Norsk (nynorsk)", "translated": t.pgettext("language name, item list", "Norwegian Nynorsk")},
    "pl": {"original": "Polski", "translated": t.pgettext("language name, item list", "Polish")},
    "pt": {"original": "Português", "translated": t.pgettext("language name, item list", "Portuguese")},
    "pt_BR": {"original": "Português do Brasil", "translated": t.pgettext("language name, item list", "Brazilian Protuguese")},
    "ro": {"original": "Română", "translated": t.pgettext("language name, item list", "Romanian")},
    "ru": {"original": "Русский", "translated": t.pgettext("language name, item list", "Russian")},
    "sk": {"original": "Slovenský", "translated": t.pgettext("language name, item list", "Slovak")},
    "sl": {"original": "Slovenski", "translated": t.pgettext("language name, item list", "Slovenian")},
    "sq": {"original": "Shqip", "translated": t.pgettext("language name, item list", "Albanian")},
    "sr": {"original": "црногорски jeзик", "translated": t.pgettext("language name, item list", "Serbian")},
    "sv": {"original": "Svenska", "translated": t.pgettext("language name, item list", "Swedish")},
    "ta": {"original": "தமிழ்", "translated": t.pgettext("language name, item list", "Tamil")},
    "th": {"original": "ไทย", "translated": t.pgettext("language name, item list", "Thai")},
    "tr": {"original": "Türkçe", "translated": t.pgettext("language name, item list", "Turkish")},
    "uk": {"original": "українська", "translated": t.pgettext("language name, item list", "Ukrainian")},
    "zh_CN": {"original": "中文（简体）", "translated": t.pgettext("language name, item list", "Chinese Simplified")},
    "zh_TW": {"original": "繁體中文", "translated": t.pgettext("language name, item list", "Chinese Traditional")}
}

#
# Create locales [ [ locale, language ], ...]
#
locales = []
language = ""
for loca in localelist.split():
    # We want each country in its own language
    setLocale(loca)
    lang = getLocaleName( loca )
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
        'he': 'wiki/מדריך_למשתמש',
        'ru': 'wiki/Руководство'
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
    qmlRegisterSingletonType(ApplicationInfo, "GCompris", 1, 0, "ApplicationInfo", ApplicationInfo.createSingleton)
    qmlRegisterType(ActivityInfo, "GCompris", 1, 0, "ActivityInfo")

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
                sys.exit(-1)
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

        except IOError:
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
    "locales": locales,
    "manual": getManual(),
    "license_info": _("This software is a GNU Package and is released under the GNU Affero General Public License."),
    "translators_names": t.pgettext("NAME OF TRANSLATORS", "Your names"),
    "public_gpg_key": '<a href="https://collaborate.kde.org/s/8GpWjyHg5xBTQFS">0x63d7264c05687d7e.asc</a>',
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

# This is to be filled for each news using the script tools/getStatusTranslations.py
translationStatus = {
    "20230329.html" : {
        "fullyTranslated": ['br', 'ca', 'ca@valencia', 'en_GB', 'es', 'eu', 'fr', 'hr', 'it', 'lt', 'nl', 'nn', 'pl', 'pt', 'pt_BR', 'ro', 'sl', 'tr', 'uk', 'zh_TW'],
        "partiallyTranslated": [['az', 99], ['be', 79], ['cs', 88], ['de', 99], ['el', 99], ['et', 99], ['fi', 94], ['he', 99], ['hu', 99], ['id', 99], ['mk', 94], ['ml', 99], ['ru', 99], ['sk', 77], ['sq', 99], ['sv', 98]]
    }
}

for filename in sorted(filenames, reverse=True):
    filename = filenames[filename]
    templateOneNews = templateEnv.get_template("newsTemplate/" + filename)
    templateVars['newsDate'] = formatDate(filename)
    templateVars['fileName'] = filename
    # Remove locale to get the status
    newsStatus = filename
    try:
        (dat, loc) = filename.split('-')
        newsStatus = dat + ".html"
    except:
        newsStatus = filename

    if newsStatus in translationStatus:
        fullLanguageTranslations = [gcomprisLocales[locale]["translated"] for locale in translationStatus[newsStatus]["fullyTranslated"]]
        partialLanguageTranslations = list(map(lambda x: [gcomprisLocales[x[0]]["translated"], x[1]], translationStatus[newsStatus]["partiallyTranslated"]))
        templateVars["fullyTranslatedLocales"] = fullLanguageTranslations
        templateVars["partiallyTranslatedLocales"] = partialLanguageTranslations

    templateVars["single_news"] = templateOneNews.render(templateVars)
    templateVars["news"].append(templateOneNews.render(templateVars))
    # read file to get the title, not sure if it is doable using jinja
    lines = ""
    with open ("newsTemplate/" + filename, 'rt', encoding='utf8') as in_file:
        for line in in_file:
            lines += line.rstrip('\n')
    rgx = re.compile('set title = [\'"](?P<name>[^{}]+)[\'"]')
    variable_names = {match.group('name') for match in rgx.finditer(lines)}

    templateNewsSingle = templateEnv.get_template("template/singlenews.html")
    outputNewsSingleText = templateNewsSingle.render(templateVars)

    minifiedHtml = htmlmin.minify(outputNewsSingleText)
    with codecs.open('news/' + templateVars['newsDate'] + suffix + '.html', 'w', encoding='utf8') as f:
        f.write(minifiedHtml)

    soup = BeautifulSoup(minifiedHtml, "html.parser")
    newsContent = soup.find_all("div", class_="newscontent")[0]
    newsContent = html.escape(str(newsContent))
    dateRFC822 = utils.formatdate(time.mktime(datetime.datetime.strptime(templateVars['newsDate'], "%Y-%m-%d").timetuple()))
    currentFeed = {"dateRFC822": dateRFC822, "date": templateVars['newsDate'], "title": next(iter(variable_names)), "description": newsContent}

    templateVars["feed"].append(currentFeed)

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

boards = sorted(boards, key=lambda t: t['title'])

# Move the menu in first position
for i in range(0, len(boards)):
    if boards[i]['name'] == 'root':
        menuScreenshot = boards[i]
        boards.pop(i)
        boards.insert(0, menuScreenshot)
        break

#
# Now process the board list
#
templateScreenshot = templateEnv.get_template("template/screenshot.html")
previousSection = ''

for screenshot in boards:
    if screenshot['section'] == '/experimental' or screenshot['name'] == 'experimental':
        continue

    templateVars["screenshot"] = screenshot
    templateVars["screenshots"].append(templateScreenshot.render(templateVars))

(opens, closes) = sectionDiff(previousSection, '')
templateVars["screenshots"].append("</div>" * closes)

templateFeedAll = templateEnv.get_template("template/feed.xml")
outputFeedAllText = templateFeedAll.render(templateVars)

with codecs.open('feed' + suffix + '.xml', 'w', encoding='utf8') as f:
    f.write(outputFeedAllText)

for f in ["christmas", "schools", "donate", "downloads", "index", "screenshots", "news", "newsall"]:
    if f == "christmas":
        templateVars["ogDescription"] = _("For Christmas, offer GCompris to your children.")
        templateVars["ogImage"] = "https://gcompris.net/images/gcompris-christmas.png"
        templateVars["ogType"] = "article"
    else:
        # If empty, it will take the page title by default
        templateVars["ogDescription"] = ""
        templateVars["ogImage"] = "https://gcompris.net/images/gcompris.png"
        templateVars["ogType"] = "website"

    template = templateEnv.get_template(os.path.join("template/", f + ".html"))
    outputText = template.render(templateVars)
    with codecs.open(f + suffix + '.html', 'w', encoding='utf8') as output:
        output.write(htmlmin.minify(outputText))

if suffix == '-en':
    template = templateEnv.get_template("template/404.html")
    outputText = template.render(templateVars)
    with codecs.open('404.html', 'w', encoding='utf8') as f:
        f.write(htmlmin.minify(outputText))
