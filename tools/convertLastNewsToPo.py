#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# GCompris - convertLastNewsToPo.py
#
# Copyright (C) 2018 Johnny Jazeix <jazeix@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.
import os
import re
import polib
import sys

newsCount = -1
if len(sys.argv) > 1:
    newsCount = -int(sys.argv[1])
print("Fetching last", -newsCount, "news")

newsFolder="news/"
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
    file = open(newsFolder+newsFileName, encoding='utf-8')
    fileContent = file.read()

    # get the title separately
    newsTitle = re.search("{% set title = \'(.+?)\'", fileContent).group(1)

    #catch all <p>: (?s)<[p>]*>(.*?)</[p>]+> in group 0
    #catch all li: <[li class="puce">]*>(.*?)</[li>]+> in group 1
    allLines = re.findall("(?s)<[p>]*>(.*?)</[p>]+>|<[li class=\"puce\">]*>(.*?)</[li>]+>", fileContent)

    titleEntry = polib.POEntry(msgid=polib.escape(newsTitle), comment='news title', msgctxt=newsFileName)
    potFile.append(titleEntry)

    for line in allLines:
        if line[0]: # paragraph
            contextEntry = polib.POEntry(msgid=polib.escape(line[0]), comment='paragraph', msgctxt=newsFileName)
            potFile.append(contextEntry)
        elif line[1]: # list item
            contextEntry = polib.POEntry(msgid=polib.escape(line[1]), comment='list item', msgctxt=newsFileName)
            potFile.append(contextEntry)

# saving the created po file
print("saving pot to", potFilename)
potFile.save(potFilename)
