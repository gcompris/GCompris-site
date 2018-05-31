#! /usr/bin/env bash
pybabel extract --add-comments=notes -F babel.cfg -o $podir/gcompris-net.pot .
python3 ./tools/convertLastNewsToPo.py && msgcat $podir/gcompris-net.pot gcompris-news.pot > gcompris-merged.pot && rm gcompris-news.pot && mv gcompris-merged.pot $podir/gcompris-net.pot
