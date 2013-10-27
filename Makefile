
VERSION = 12.11

ALL_LINGUAS = br cs el es gd lt pt_BR sl hu de fr sr gl pl sk ta ru th bg da zh_TW lv nn sv
#ALL_LINGUAS = fr

POFILES=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang.po "; done)

CATALOGS=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang.mo  "; done)

sources = \
	gcompris.py \
	template/base.html \
	template/buy.html \
	template/download_macosx.html \
	template/index.html \
	template/news.html \
	template/newsall.html \
	template/onenews.html \
	template/screenshot.html \
	template/screenshots.html \
	template/social.html \
	template/test.html

i18_sources = template/base.html \
	template/buy.html \
	template/index.html

all:
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  ./gcompris.py $(VERSION) $$lang "$(ALL_LINGUAS)"; \
	done; \
	./gcompris.py $(VERSION) en "$(ALL_LINGUAS)"

update:
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  if test locale/messages.pot -nt locale/$$lang.po; then \
	    cd locale; intltool-update --dist --gettext-package=messages $$lang; cd ..; \
	  fi; \
	  header_end=`grep -n '^$$' locale/$$lang.po | head -1 | sed s/://`; \
	  tail -n +$$header_end locale/$$lang.po > locale/tempfile; \
	  mkdir -p locale/$$lang/LC_MESSAGES; \
	  cat ~/Projets/gcompris/po/$$lang.po locale/tempfile > locale/$$lang/LC_MESSAGES/gcompris.po; \
	  rm -f locale/tempfile; \
	  msgfmt locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
	done;

extract: $(i18_sources)
	pybabel extract -F babel.cfg -o locale/messages.pot ./
	if test $(shell git diff locale/messages.pot | grep "^+[^+]" | wc -l) -eq 1; then \
	  git checkout locale/messages.pot; \
	  touch locale/messages.pot; \
	fi

#%.po :
#	pybabel init -d locale -l `echo $* | cut -d/ -f2` -i locale/messages.pot -o $*.po

online:
	rsync -az --copy-unsafe-links --exclude .git . bdoin@gcompris.net:/var/www/

clean:
	rm -f *.html *.pyc
