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
* python 3.8
* subversion
* Jinja2
* PyQt5 (QtCore and QtQml)
* htmlmin
* beautifulsoup4

To test the site locally, you need to copy the content of https://gcompris.net/fonts/ in a fonts folder at the root of the repository. It contains the fonts Acme (https://fonts.google.com/specimen/Acme), Noto Sans latin (https://fonts.gstatic.com/s/notosans/v27/o-0IIpQlx3QUlC5A4PNr5TRA.woff2), Noto Sans latin-ext (https://fonts.gstatic.com/s/notosans/v27/o-0IIpQlx3QUlC5A4PNr6zRAW_0.woff2) and Noto Sans Malayalam (https://fonts.google.com/noto/specimen/Noto+Sans+Malayalam), all in woff2, woff and ttf formats. Those fonts are under the OFL license (https://opensource.org/licenses/OFL-1.1). Other languages will use the corresponding default sans-serif font from the system.

## Build this website

```bash
git clone git@invent.kde.org:websites/gcompris-net.git
cd gcompris-net/screenshots_qt; ./small_middle_converter.sh; cd ..
make clean update all
```

The update target will get the GCompris corresponding tarball source version from https://gcompris.net/download/qt/src/ and uncompress it in the website folder if not already present.
