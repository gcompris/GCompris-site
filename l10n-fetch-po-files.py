#!/usr/bin/python
#
# GCompris - l10n-fetch-po-files.py
#
# Copyright (C) 2015 Trijita org <jktjkt@trojita.org>
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
import sys
import subprocess

# Copied from Trojita
"""Fetch the .po files from KDE's SVN for GCompris-net

Run me from GCompris's top-level directory.
"""


SVN_PATH = "svn://anonsvn.kde.org/home/kde/trunk/l10n-kf5/"
SOURCE_PO_PATH = "/messages/www/gcompris_net.po"
OUTPUT_PO_PATH = "./locale/"
OUTPUT_PO_PATTERN = "%s.po"

fixer = re.compile(r'^#~\| ', re.MULTILINE)
re_empty_msgid = re.compile('^msgid ""$', re.MULTILINE)
re_empty_line = re.compile('^$', re.MULTILINE)
re_has_qt_contexts = re.compile('X-Qt-Contexts: true\\n')

if not os.path.exists(OUTPUT_PO_PATH):
    os.mkdir(OUTPUT_PO_PATH)

all_languages = sys.argv[1]
all_languages = [x.strip() for x in all_languages.split(" ") if len(x)]

for lang in all_languages:
    print lang
    try:
        raw_data = subprocess.check_output(['svn', 'cat', SVN_PATH + lang + SOURCE_PO_PATH],
                                          stderr=subprocess.PIPE)
        (transformed, subs) = fixer.subn('# ~| ', raw_data)
        pos1 = re_empty_msgid.search(transformed).start()
        pos2 = re_empty_line.search(transformed).start()
        if re_has_qt_contexts.search(transformed, pos1, pos2) is None:
            transformed = transformed[:pos2] + \
                    '"X-Qt-Contexts: true\\n"\n' + \
                    transformed[pos2:]
            subs = subs + 1
        if (subs > 0):
            print "Fetched %s (and performed %d cleanups)" % (lang, subs)
        else:
            print "Fetched %s" % lang
        file(OUTPUT_PO_PATH + OUTPUT_PO_PATTERN % lang, "wb").write(transformed)
    except subprocess.CalledProcessError:
        print "No data for %s" % lang
