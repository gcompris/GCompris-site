
VERSION = 12.11

ALL_LINGUAS = cs el es lt pt_BR sl hu de fr sr gl pl sk ta ru th bg da zh_TW lv nn sv
#ALL_LINGUAS = fr

POFILES=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang/LC_MESSAGES/messages.po "; done)

CATALOGS=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang/LC_MESSAGES/messages.mo  "; done)

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

all: index-en.html

locale/messages.pot : $(i18_sources)
	pybabel extract -F babel.cfg -o locale/messages.pot ./
	if test $(shell git diff locale/messages.pot | grep "^+[^+]" | wc -l) -eq 1; then \
	  git checkout locale/messages.pot; \
	  touch locale/messages.pot; \
	fi

#%.po :
#	pybabel init -d locale -l `echo $* | cut -d/ -f2` -i locale/messages.pot -o $*.po

index-en.html : $(POFILES) locale/messages.pot $(sources)
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  dir=locale/$$lang/LC_MESSAGES; \
	  if test locale/messages.pot -nt locale/$$lang/LC_MESSAGES/messages.po; then \
	    pybabel update --previous -l $$lang -d locale -i locale/messages.pot; \
	  fi; \
	  cat ~/Projets/gcompris/po/$$lang.po locale/$$lang/LC_MESSAGES/messages.po > locale/$$lang/LC_MESSAGES/gcompris.po; \
	  pybabel compile -f -d locale -i locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
	  ./gcompris.py $(VERSION) $$lang "$(ALL_LINGUAS)"; \
	done; \
	./gcompris.py $(VERSION) en "$(ALL_LINGUAS)"

clean:
	rm -f *.html *.pyc
