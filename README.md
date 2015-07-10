GCompris-site
=============

The [GCompris Web Site](http://gcompris.net) is developped in Python
with [Jinja2](http://jinja.pocoo.org/docs/dev/) templating engine in
Python. The pages are created staticaly at build time and pushed on
the web server.

The *gcompris.py* script creates the pages from Jinja2 templates and
takes data from the GCompris application to get the list of activities
and their description. With these information, it creates the
[screenshot page](http://gcompris.net/screenshots-en.html) in all the
languages supported.

The official repository is [hosted by
KDE](http://quickgit.kde.org/?p=websites%2Fgcompris-net.git)
