
VERSION = 15.10

ALL_LINGUAS = bg br cs da de el es fr gd gl hu it lt lv nl nn pl pt_BR ru sk sl sr sv ta th zh_TW 
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
	./gcompris.py $(VERSION) en "$(ALL_LINGUAS)"; \
	cp template/mobile-privacy-policy.html .

#
# Run it to update the translation. This requires the Gtk+ version.
update:
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  if test ! -f locale/$$lang.po; then \
	    cp locale/messages.pot locale/$$lang.po; \
	    touch -d yesterday locale/$$lang.po; \
	  fi; \
	  if test locale/messages.pot -nt locale/$$lang.po; then \
	    cd locale; intltool-update --dist --gettext-package=messages $$lang; cd ..; \
	  fi; \
	  header_end=`grep -n '^$$' locale/$$lang.po | head -1 | sed s/://`; \
	  tail -n +$$header_end locale/$$lang.po > locale/tempfile; \
	  mkdir -p locale/$$lang/LC_MESSAGES; \
	  cat ~/Projets/gcompris/gcompris-gtk/po/$$lang.po locale/tempfile | grep -v "^#~" > locale/$$lang/LC_MESSAGES/gcompris.po; \
	  rm -f locale/tempfile; \
	  msgfmt locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
	done;
#
# Run this when new strings are added in the templates
extract: $(i18_sources)
	pybabel extract -F babel.cfg -o locale/messages.pot ./
	if test $(shell git diff locale/messages.pot | grep "^+[^+]" | wc -l) -eq 1; then \
	  git checkout locale/messages.pot; \
	  touch locale/messages.pot; \
	fi

#%.po :
#	pybabel init -d locale -l `echo $* | cut -d/ -f2` -i locale/messages.pot -o $*.po

online:
	rsync -az --copy-unsafe-links --exclude .git --exclude .rcc --exclude template . maintener@gcompris.net:/var/www/

clean:
	rm -f *.html *.pyc
