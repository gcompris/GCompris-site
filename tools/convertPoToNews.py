#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re
import polib
import sys
import os.path

if len(sys.argv) < 3:
    print('Usage : python3 convertPoToNews.py locale file.po.')
    sys.exit(1)

locale = sys.argv[1]
poFile = polib.pofile(sys.argv[2], encoding="utf-8")

news = {}

for entry in poFile:
    filename = entry.msgctxt
    if not filename or not filename.find('.html'):
        continue
    index = filename.find('.html')
    filename = "news/" + filename[:index] + '-' + locale + filename[index:]

    if os.path.isfile(filename):
        print(filename + " already exists, we skip it")
        continue

    context = entry.tcomment

    currentNews = {}
    if news.get(filename):
        currentNews = news.get(filename)

    if "title" in context:
        currentNews['title'] = entry.msgstr
        currentNews['header'] = "{% extends \"template/onenews.html\" %}\n" \
                                "{% set title = '" + entry.msgstr + "' %}\n" \
                                "{% set withlongcontent = 0 %}\n" \
                                "{% block content %} \n"
    else:
        currentNews["newsContent"] = polib.unescape(entry.msgstr)

    news[filename] = currentNews

FOOTER = "{% endblock %}"
for currentNews in news:
    if news[currentNews]['title'] == "" or news[currentNews]['newsContent'] == "":
        print("Skip news", currentNews)
        continue
    
    print("Creating", currentNews)
    file = open(currentNews, "w", encoding="utf-8")
    file.write(news[currentNews]['header'])
    file.write(news[currentNews]['newsContent'])
    file.write(FOOTER+"\n")
