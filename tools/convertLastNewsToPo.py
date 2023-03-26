#!/usr/bin/python3
#
# GCompris - convertLastNewsToPo.py
#
# SPDX-FileCopyrightText: 2018 Johnny Jazeix <jazeix@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import sys
import polib

newsCount = -1
if len(sys.argv) > 1:
    newsCount = -int(sys.argv[1])
print("Fetching last", -newsCount, "news")

newsFolder="newsTemplate/"
# get all the news in news folder and only get the last N ones that are not translated
lastNews = [news for news in sorted(os.listdir(newsFolder)) if not "-" in news and "html" in news][newsCount:]

# directly append to $podir/gcompris-net.pot if it exists, else create a new
# pot file
potFilename = ''
if os.path.isfile(os.path.expandvars('$podir/gcompris-net.pot')):
    potFilename = os.path.expandvars('$podir/gcompris-net.pot')
potFile = polib.pofile(potFilename, encoding="utf-8")
if potFilename == '':
    potFilename = 'gcompris-news.pot'
    potFile.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'gcompris-devel@kde.org',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

for newsFileName in lastNews:
    print("working on", newsFolder+newsFileName)
    with open(newsFolder+newsFileName, encoding='utf-8') as file:
        fileContent = file.read()

    # get the title separately
    newsTitle = re.search("{% set title = '(.+?)' %}", fileContent).group(1)
    # Eval in case there is a \' in the title string to unescape
    newsTitle = eval("'%s'" % (newsTitle,))

    #catch all <p>: (?s)<p>(.*?)</p> in group 0
    #catch all li: <li.*?>(.*?)</li> in group 1
    allLines = re.findall("(?s)<p>(.*?)</p>|<li.*?>(.*?)</li>", fileContent)

    titleEntry = polib.POEntry(msgid=polib.escape(newsTitle), comment='news title', msgctxt=newsFileName)
    potFile.append(titleEntry)

    for line in allLines:
        if line[0]: # paragraph
            contextEntry = polib.POEntry(msgid=polib.escape(line[0]), comment='paragraph', msgctxt=newsFileName)
            potFile.append(contextEntry)
        elif line[1]: # list item
            if line[1] == "{{ oneLocale }}":
                contextEntry = polib.POEntry(msgid=polib.escape(line[1]), comment='Keep this string as this, it corresponds to the language name', msgctxt=newsFileName)
            if line[1] == "{{ oneLocale }} ({{ oneStatus }}%)":
                contextEntry = polib.POEntry(msgid=polib.escape(line[1]), comment='The arguments are the language name and its percentage of completion. Keep the entries {{ oneLocale }} and {{ oneStatus }} as this, only move the % and/or reverse the order if needed for your locale.', msgctxt=newsFileName)
            else:
                contextEntry = polib.POEntry(msgid=polib.escape(line[1]), comment='list item', msgctxt=newsFileName)
            potFile.append(contextEntry)

# saving the created po file
print("saving pot to", potFilename)
potFile.save(potFilename)
