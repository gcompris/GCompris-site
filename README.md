GCompris-site
=============

The [GCompris Web Site](https://gcompris.net) is developed in Python
with [Jinja2](https://jinja.palletsprojects.com/en/master/) templating engine in
Python. The pages are created statically at build time and pushed on
the web server.

The *gcompris.py* script creates the pages from Jinja2 templates and
takes data from the GCompris application to get the list of activities
and their description. With these information, it creates the
[screenshot page](https://gcompris.net/screenshots-en.html) in all the
languages supported.

The official repository is [hosted by
KDE](https://invent.kde.org/websites/gcompris-net)

## Requirements
* Jinja2
* PyQt5 (QtCore and QtQml)

## Build this website

```bash
git clone git@invent.kde.org:education/gcompris.git
git clone git@invent.kde.org:websites/gcompris-net.git
cd gcompris; git checkout KDE/2.0; cd ..
cd gcompris-net/screenshots_qt; ./small_middle_converter.sh; cd ..
GCOMPRIS_DIR=../gcompris make clean update all
````
