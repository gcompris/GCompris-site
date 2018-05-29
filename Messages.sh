#! /usr/bin/env bash
pybabel extract --add-comments=notes -F babel.cfg -o $podir/gcompris-net.pot .
python3 ./tools/convertLastNewsToPo.py && msgcat $podir/gcompris-net.pot gcompris-news.pot > $podir/gcompris-merged.pot && mv gcompris-merged.pot gcompris-net.pot && rm gcompris-news.pot
