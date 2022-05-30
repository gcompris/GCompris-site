#! /bin/sh

# SPDX-FileCopyrightText: 2022 Johnny Jazeix <jazeix@gmail.com>
# SPDX-License-Identifier: BSD-2-Clause

if [ ! -d "newsTemplate/" ]; then
    echo "Needs to be run from top level directory of gcompris-net"
    exit -1
fi
    
fileUpdated=0
cd newsTemplate/
# Added files
for f in `git ls-files -o`; do
    date=${f%-*}; # Remove everything after the date (everything after -, included)
    locale=${f#*-} # Remove everything before the date (everything before -, included)
    locale=${locale%.*} # Remove the extension (everything after ., included)
    git add $f && git commit -m "add $date news for $locale"
    fileUpdated=1
done

# Modified files
for f in `git ls-files -m`; do
    date=${f%-*}; # Remove everything after the date (everything after -, included)
    locale=${f#*-} # Remove everything before the date (everything before -, included)
    locale=${locale%.*} # Remove the extension (everything after ., included)
    git add $f && git commit -m "update $date news for $locale"
    fileUpdated=1
done

exit $fileUpdated
