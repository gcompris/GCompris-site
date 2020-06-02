GCompris-site
=============

The [GCompris Web Site](https://gcompris.net) is developped in Python
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
