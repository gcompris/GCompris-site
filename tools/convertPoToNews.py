#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# GCompris - convertPoToNews.py
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

if len(sys.argv) < 3:
    print('Usage : python3 convertPoToNews.py locale file.po.')
    sys.exit(1)

locale = sys.argv[1]
poFilename=sys.argv[2]
if not os.path.isfile(poFilename):
    print(poFilename, "does not exist, we cannot create news files for", locale)
    sys.exit(1)

poFile = polib.pofile(poFilename, encoding="utf-8")

news = {}

ignoredNews = []
# reading all news translations from the po
# storing them in a dict
for entry in poFile:
    originalNewsFilename = entry.msgctxt

    if "fuzzy" in entry.flags:
        continue

    if not originalNewsFilename or not originalNewsFilename.find('.html'):
        continue
    originalFilename = "newsTemplate/" + originalNewsFilename
    index = originalNewsFilename.find('.html')
    newsFilename = "newsTemplate/" + originalNewsFilename[:index] + '-' + locale + originalNewsFilename[index:]

    # if the news has been ignored because at least one string not translated
    if newsFilename in ignoredNews:
        continue

    # Check if the news is 100% translated, else skip it
    isFullyTranslated = True
    for allEntries in poFile:
        if allEntries.msgctxt == originalNewsFilename and (allEntries.msgstr == "" or "fuzzy" in entry.flags):
            print("Skip", newsFilename, "due to", allEntries.msgid, "not translated")
            isFullyTranslated = False
            ignoredNews.append(newsFilename)
            break
    if not isFullyTranslated:
        continue

    currentNews = {}
    if news.get(newsFilename):
        currentNews = news.get(newsFilename)

    context = entry.comment
    if "title" in context:
        currentNews['title'] = entry.msgstr
        currentNews['originalFilename'] = originalFilename
    else:
        currentNews[polib.unescape(entry.msgid)] = polib.unescape(entry.msgstr)

    news[newsFilename] = currentNews
# for all news we have in the pot file, we create the corresponding html 
# translated file
for currentNews in news:
    if not 'title' in news[currentNews] or news[currentNews]['title'] == "":
        print("Skip news", currentNews)
        continue

    print("Creating", currentNews)

    # Read in the file
    with open(news[currentNews]['originalFilename'], "r", encoding="utf-8") as originalFile:
        fileData = originalFile.read()

    # Replace the target string
    for string in news[currentNews]:
        if 'title' == string:
            matches = re.findall(r"{% set title = \'(.+?)\'", fileData)
            for m in matches:
                fileData = fileData.replace('\'%s\'' % m, '\'%s\'' % news[currentNews][string])
            continue
        else:
            # We only want to replace the first occurence of the string
            fileData = fileData.replace(string, news[currentNews][string], 1)

    # Write the file out again
    with open(currentNews, 'w') as file:
        file.write(fileData)
