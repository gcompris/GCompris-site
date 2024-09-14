# -* coding: utf-8 -*-
#!/usr/bin/python3
#
# GCompris - getStatusTranslations.py
#
# SPDX-FileCopyrightText: 2023-2024 Johnny Jazeix <jazeix@gmail.com>
#
#   SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import polib

from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtQml import QQmlComponent, QQmlEngine

if len(sys.argv) < 2:
    print('Usage : python3 getStatusTranslations.py gcomprisPath')
    sys.exit(1)

gcomprisPath = sys.argv[1]
if not os.path.isdir(gcomprisPath):
    print("GCompris path not correct")
    sys.exit(1)

pathToLanguageList=os.path.join(gcomprisPath, "src/core/LanguageList.qml")

app = QCoreApplication(sys.argv)
engine = QQmlEngine()
component = QQmlComponent(engine)
try:
    component.loadUrl(QUrl(pathToLanguageList))
    languageListComponent = component.create()
except IOError:
    pass
supportedLanguageList = list(map(lambda element: element["locale"].replace(".UTF-8", ""), languageListComponent.property("languages").toVariant()))

# Append short names
supportedLanguageList = supportedLanguageList + list(map(lambda element: element.split("_")[0], supportedLanguageList))

fullyTranslated = []
partiallyTranslated = []
for root, dirs, files in os.walk(os.path.join(gcomprisPath, "poqm")):
    for name in files:
        if name.endswith(".po"):
            poFile = polib.pofile(os.path.join(root, name), encoding='utf-8')
            not_translated = len([e for e in poFile if not e.obsolete])
            translated = round(len(poFile.translated_entries()) * 100 / not_translated)
            lang = os.path.basename(os.path.normpath(root))
            if lang == "en":
                continue
            if not lang in supportedLanguageList:
                #print("ignore", lang)
                continue
            if translated == 100:
                fullyTranslated.append(lang)
            else:
                partiallyTranslated.append([lang, translated])
fullyTranslated.sort()
partiallyTranslated.sort()
print(f'"fullyTranslated": {fullyTranslated},')
print(f'"partiallyTranslated": {partiallyTranslated}')
