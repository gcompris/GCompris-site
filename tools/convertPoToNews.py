#!/usr/bin/python3
#
# GCompris - convertPoToNews.py
#
# SPDX-FileCopyrightText: 2018 Johnny Jazeix <jazeix@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import sys
import polib

if len(sys.argv) < 3:
    print('Usage : python3 convertPoToNews.py locale file.po.')
    sys.exit(1)

locale = sys.argv[1]
poFilename = sys.argv[2]
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

    if "fuzzy" in entry.flags or entry.obsolete:
        continue

    if not originalNewsFilename or originalNewsFilename.find('.html') == -1:
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
for currentKey, currentNews in news.items():
    if 'title' not in currentNews or currentNews['title'] == "":
        print("Skip news", currentKey)
        continue

    print("Creating", currentKey)

    # Read in the file
    with open(currentNews['originalFilename'], "r", encoding="utf-8") as originalFile:
        fileData = originalFile.read()

    # Check first all the strings of the file are translated (po files may be out of sync)
    isFullyTranslated = True
    allLines = re.findall("(?s)<p>(.*?)</p>|<li.*?>(.*?)</li>", fileData)
    for line in allLines:
        if line[0]: # paragraph
            if not line[0] in currentNews:
                print(f"Skip news {currentKey} because {line[0]} not translated")
                isFullyTranslated = False
                break
        elif line[1]: # list item
            if not line[1] in currentNews:
                print(f"Skip news {currentKey} because {line[1]} not translated")
                isFullyTranslated = False
                break
    if not isFullyTranslated:
        continue

    # Replace the target string
    for string in currentNews:
        if 'title' == string:
            matches = re.findall(r"{% set title = '(.+?)' %}", fileData)
            for m in matches:
                fileData = fileData.replace('\'%s\'' % m.replace("'", "\\'"), repr(currentNews[string]))
            continue
        # We only want to replace the first occurence of the string
        fileData = fileData.replace(string, currentNews[string], 1)

    # Write the file out again
    with open(currentKey, 'w', encoding='utf8') as file:
        file.write(fileData)
