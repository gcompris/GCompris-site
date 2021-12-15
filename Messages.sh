#! /usr/bin/env bash
pybabel extract --add-comments=notes -F babel.cfg -o $podir/gcompris-net.pot .
python3 ./tools/convertLastNewsToPo.py 2
