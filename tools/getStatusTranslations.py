# -* coding: utf-8 -*-
#!/usr/bin/python3
#
# GCompris - getStatusTranslations.py
#
# SPDX-FileCopyrightText: 2023 Johnny Jazeix <jazeix@gmail.com>
#
#   SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import polib

if len(sys.argv) < 2:
    print('Usage : python3 getStatusTranslations.py gcomprisPath')
    sys.exit(1)

gcomprisPath = sys.argv[1]
if not os.path.isdir(gcomprisPath):
    print("GCompris path not correct")
    sys.exit(1)

fullyTranslated = []
partiallyTranslated = []
for root, dirs, files in os.walk(os.path.join(gcomprisPath, "poqm")):
    for name in files:
        if name.endswith(".po"):
            poFile = polib.pofile(os.path.join(root, name), encoding='utf-8')
            translated = poFile.percent_translated()
            lang = os.path.basename(os.path.normpath(root))
            if lang == "en":
                continue
            if translated == 100:
                fullyTranslated.append(lang)
            else:
                partiallyTranslated.append([lang, translated])
fullyTranslated.sort()
partiallyTranslated.sort()
print(f'"fullyTranslated": {fullyTranslated},')
print(f'"partiallyTranslated": {partiallyTranslated}')
