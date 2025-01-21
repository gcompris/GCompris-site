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
import requests
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
def set_locale(locale_name):
    global _
    global t
    t = gettext.translation('gcompris', 'po', languages=[locale_name], fallback=True)
    _ = t.gettext

def format_date(date):
    return date[0:4] + '-' + date[4:6] + '-' + date[6:8]

# Set the default locale
set_locale(locale)

gcomprisLocales = {
    "en_GB": {"original": "UK English", "translated": t.pgettext("language name, item list", "UK English")},
    "en_US": {"original": "American English", "translated": t.pgettext("language name, item list", "American English")},
    "ar": {"original": "العربية", "translated": t.pgettext("language name, item list", "Arabic")},
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
    "eo": {"original": "Esperanto", "translated": t.pgettext("language name, item list", "Esperanto")},
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
    "ka": {"original": "ქართული", "translated": t.pgettext("language name, item list", "Georgian")},
    "ko": {"original": "한국어", "translated": t.pgettext("language name, item list", "Korean")},
    "lt": {"original": "Lietuvių", "translated": t.pgettext("language name, item list", "Lithuanian")},
    "lv": {"original": "Latviešu", "translated": t.pgettext("language name, item list", "Latvian")},
    "mk": {"original": "Македонски", "translated": t.pgettext("language name, item list", "Macedonian")},
    "ml": {"original": "മലയാളം", "translated": t.pgettext("language name, item list", "Malayalam")},
    "nl": {"original": "Nederlands", "translated": t.pgettext("language name, item list", "Dutch")},
    "nn": {"original": "Norsk (nynorsk)", "translated": t.pgettext("language name, item list", "Norwegian Nynorsk")},
    "pl": {"original": "Polski", "translated": t.pgettext("language name, item list", "Polish")},
    "pt": {"original": "Português", "translated": t.pgettext("language name, item list", "Portuguese")},
    "pt_BR": {"original": "Português do Brasil", "translated": t.pgettext("language name, item list", "Brazilian Portuguese")},
    "ro": {"original": "Română", "translated": t.pgettext("language name, item list", "Romanian")},
    "ru": {"original": "Русский", "translated": t.pgettext("language name, item list", "Russian")},
    "sa": {"original": "संस्कृतम्", "translated": t.pgettext("language name, item list", "Sanskrit")},
    "sk": {"original": "Slovenský", "translated": t.pgettext("language name, item list", "Slovak")},
    "sl": {"original": "Slovenski", "translated": t.pgettext("language name, item list", "Slovenian")},
    "sq": {"original": "Shqip", "translated": t.pgettext("language name, item list", "Albanian")},
    "sr": {"original": "црногорски jeзик", "translated": t.pgettext("language name, item list", "Serbian")},
    "sv": {"original": "Svenska", "translated": t.pgettext("language name, item list", "Swedish")},
    "sw": {"original": "Kiswahili", "translated": t.pgettext("language name, item list", "Swahili")},
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
for loca in localelist.split():
    lang = gcomprisLocales[loca]["original"]
    locales.append([loca, lang])
# Add en_US manually
locales.append(['en', gcomprisLocales['en_US']["original"]])
locales = sorted(locales, key=lambda t: t[1])

# Special case for en
language = gcomprisLocales[locale]["original"] if locale in gcomprisLocales else 'English'

suffix = '-' + locale

#
# We don't have a translation of each manual. If we have it
# we return it else we return the english one
def get_manual():
    r = requests.head('https://gcompris.net/docbook/stable5/' + locale + '/index.html')
    if r.ok:
        return locale
    return 'en'

descriptions = []

def get_boards():
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
            activity_info = component.create()
            if activity_info is None:
                # Print all errors that occurred.
                for error in component.errors():
                    print(error.toString())
                sys.exit(-1)
            # ignore disabled activities
            if not activity_info.property('enabled'):
                print("Disabling", activity_info.property('name'))
                continue
            description = activity_info.property('description').replace('\n', '<br/>')
            name = activity_info.property('name').split('/')[0]
            title = activity_info.property('title')
            credit = activity_info.property('credit').replace('\n', '<br/>')
            goal = activity_info.property('goal').replace('\n', '<br/>')
            section = activity_info.property('section')
            author = activity_info.property('author')
            if 'Timothée Giet' in author or author == "":
                author = re.sub("&lt;.*?&gt;", "", author)
            else:
                author = re.sub("&lt;.*?&gt;", "", author)+(' & Timothée Giet')

            manual = activity_info.property('manual').replace('\n', '<br/>')
            difficulty = activity_info.property('difficulty')
            category = activity_info.property('category')
            prerequisite = activity_info.property('prerequisite').replace('\n', '<br/>')
            if name != "menu":
                icon = activity_info.property('icon').split('/')[1]

            infos = {'description': description,
                     'name': name,
                     'title': title,
                     'credit': credit,
                     'goal': goal,
                     'section': section,
                     'author': author,
                     'manual': manual,
                     'difficulty': difficulty,
                     'type': category,
                     'prerequisite': prerequisite,
                     'icon': icon}
            descriptions.append(infos)

        except IOError:
            pass

    return descriptions

templateLoader = jinja2.FileSystemLoader(searchpath=".")
templateEnv = jinja2.Environment(loader=templateLoader,
                                 extensions=['jinja2.ext.i18n'],
                                 trim_blocks=True,
                                 lstrip_blocks=True)
templateEnv.install_gettext_callables(t.gettext, t.ngettext, newstyle=True, pgettext=t.pgettext)

# Specify any input variables to the template as a dictionary.
templateVars = {
    "locale": locale,
    "direction": "rtl" if locale in ("ar", "he") else "ltr",
    "suffix": suffix,
    "language": language,
    "revision_date": today.strftime("%Y-%m-%d"),
    "current_year": today.strftime("%Y"),
    "version": version,
    "news": [],
    "single_news": [],
    "screenshots": [],
    "locales": locales,
    "manual": get_manual(),
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
    except ValueError:
        if filename_noext not in filenames:
            filenames[filename_noext] = filename

# This is to be filled for each news using the script tools/getStatusTranslations.py
translationStatus = {
    "20230329.html": {
        "fullyTranslated": ['br', 'ca', 'ca@valencia', 'el', 'en_GB', 'es', 'eu', 'fr', 'hr', 'it', 'lt', 'ml', 'nl', 'nn', 'pl', 'pt', 'pt_BR', 'ro', 'sl', 'tr', 'uk', 'zh_TW'],
        "partiallyTranslated": [['az', 99], ['be', 79], ['cs', 88], ['de', 99], ['et', 99], ['fi', 94], ['he', 99], ['hu', 99], ['id', 99], ['mk', 94], ['ru', 99], ['sk', 77], ['sq', 99], ['sv', 98]]
    },
    "20230606.html": {
        "fullyTranslated": ['ar', 'az', 'br', 'ca', 'ca@valencia', 'el', 'en_GB', 'es', 'eu', 'fr', 'hr', 'id', 'it', 'lt', 'ml', 'nl', 'nn', 'pl', 'pt', 'pt_BR', 'ro', 'sl', 'tr', 'uk'],
        "partiallyTranslated": [['be', 79], ['cs', 88], ['de', 99], ['eo', 99], ['et', 99], ['fi', 98], ['he', 99], ['hu', 99], ['mk', 94], ['ru', 99], ['sk', 87], ['sq', 99], ['sv', 98], ['zh_TW', 99]]
    },
    "20240221.html": {
        "fullyTranslated": ['ar', 'bg', 'br', 'ca', 'ca@valencia', 'el', 'es', 'eu', 'fr', 'gl', 'hr', 'hu', 'it', 'lt', 'ml', 'nl', 'pl', 'pt_BR', 'ro', 'sl', 'tr', 'uk'],
        "partiallyTranslated": [['az', 97], ['be', 86], ['cs', 94], ['de', 95], ['en_GB', 95], ['eo', 99], ['et', 95], ['fi', 94], ['he', 95], ['id', 95], ['mk', 90], ['nn', 95], ['pt', 95], ['ru', 95], ['sk', 83], ['sq', 99], ['sv', 95], ['sw', 99], ['zh_TW', 95]]
    },
    "20240523.html": {
        "fullyTranslated": ['ar', 'bg', 'br', 'ca', 'ca@valencia', 'el', 'es', 'eu', 'fr', 'gl', 'hr', 'hu', 'it', 'lt', 'ml', 'nl', 'nn', 'pl', 'pt_BR', 'ro', 'ru', 'sl', 'sv', 'tr', 'uk'],
"partiallyTranslated": [['az', 97], ['be', 86], ['cs', 95], ['de', 95], ['en_GB', 95], ['eo', 99], ['et', 95], ['fi', 94], ['he', 95], ['id', 99], ['mk', 90], ['pt', 95], ['sk', 83], ['sq', 99], ['sw', 99], ['zh_TW', 95]]
    },
    "20240920.html": {
        "fullyTranslated": ['ar', 'bg', 'br', 'ca', 'ca@valencia', 'el', 'en_GB', 'eo', 'es', 'eu', 'fr', 'gl', 'hr', 'hu', 'id', 'it', 'lt', 'lv', 'ml', 'nl', 'nn', 'pl', 'pt_BR', 'ro', 'ru', 'sl', 'sq', 'sv', 'sw', 'tr', 'uk'],
        "partiallyTranslated": [['az', 97], ['be', 87], ['cs', 97], ['de', 96], ['et', 96], ['fi', 95], ['he', 96], ['mk', 90], ['pt', 96], ['sk', 84], ['zh_TW', 96]]
    },
    "20241129.html": {
        "fullyTranslated": ['ar', 'bg', 'br', 'ca', 'ca@valencia', 'el', 'en_GB', 'eo', 'es', 'eu', 'fr', 'gl', 'hr', 'hu', 'id', 'it', 'lt', 'lv', 'ml', 'nl', 'nn', 'pl', 'pt_BR', 'ro', 'ru', 'sl', 'sq', 'sv', 'sw', 'tr', 'uk'],
        "partiallyTranslated": [['az', 97], ['be', 87], ['cs', 97], ['de', 96], ['et', 96], ['fi', 95], ['he', 96], ['mk', 90], ['pt', 96], ['sk', 84], ['zh_TW', 96]]
    }
}

for filename in sorted(filenames, reverse=True):
    filename = filenames[filename]
    templateOneNews = templateEnv.get_template("newsTemplate/" + filename)
    templateVars['newsDate'] = format_date(filename)
    templateVars['fileName'] = filename
    # Remove locale to get the status
    newsStatus = filename
    try:
        (dat, loc) = filename.split('-')
        newsStatus = dat + ".html"
    except ValueError:
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
    with open("newsTemplate/" + filename, 'rt', encoding='utf8') as in_file:
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
boards = get_boards()

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

for screenshot in boards:
    if screenshot['section'] == '/experimental' or screenshot['name'] == 'experimental':
        continue

    templateVars["screenshot"] = screenshot
    templateVars["screenshots"].append(templateScreenshot.render(templateVars))

templateFeedAll = templateEnv.get_template("template/feed.xml")
outputFeedAllText = templateFeedAll.render(templateVars)

with codecs.open('feed' + suffix + '.xml', 'w', encoding='utf8') as f:
    f.write(outputFeedAllText)

for f in ["christmas", "schools", "donate", "downloads", "index", "screenshots", "news", "newsall", "faq"]:
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
