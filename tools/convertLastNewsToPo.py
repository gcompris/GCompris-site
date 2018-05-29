#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import polib
import sys

newsCount = -1
if len(sys.argv) > 1:
    newsCount = -int(sys.argv[1])
print("Fetching last", -newsCount, "news")

# get all the news in news folder and only get the last N ones that are not translated
lastNews = [news for news in sorted(os.listdir("news")) if not "-" in news and "html" in news][newsCount:]

potFile = polib.pofile('', encoding="utf-8")
potFile.metadata = {
    'Project-Id-Version': '1.0',
    'Report-Msgid-Bugs-To': 'gcompris-devel@kde.org',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Transfer-Encoding': '8bit',
}

for newsFileName in lastNews:
    print(newsFileName)
    file = open("news/"+newsFileName, encoding='utf-8')
    fileContent = file.readlines()
    newsText = []
    for line in fileContent:
        if 'set title' in line:
            newsTitle = re.search("\'(.+?)\'", line).group(1)
        if not "{%" in line: # remove jinja2 expressions
            newsText.append(line)
    titleEntry = polib.POEntry(msgid=polib.escape(newsTitle), tcomment='news title', msgctxt=newsFileName)
    potFile.append(titleEntry)

    text = ''.join(newsText)
    contextEntry = polib.POEntry(msgid=polib.escape(text), tcomment='news text', msgctxt=newsFileName)
    potFile.append(contextEntry)

# saving the created po file
potFile.save('gcompris-news.pot')
