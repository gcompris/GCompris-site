
VERSION = 1.0

ALL_LINGUAS = be br ca ca@valencia de el es et eu fi fr ga gd gl he hi hu id it ko lt ml nl nn pl pt pt_BR ro ru sk sl sv tr uk zh_CN zh_TW
#ALL_LINGUAS = fr

POFILES=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang.po "; done)

CATALOGS=$(shell LINGUAS="$(ALL_LINGUAS)"; for lang in $$LINGUAS; do printf "locale/$$lang.mo  "; done)

HTML := $(ALL_LINGUAS:%=index-%.html)

sources = \
	gcompris.py \
	template/base.html \
	template/christmas.html \
	template/donate.html \
	template/downloads.html \
	template/download_macosx.html \
	template/index.html \
	template/news.html \
	template/newsall.html \
	template/onenews.html \
	template/screenshot.html \
	template/screenshots.html \
	template/test.html

i18_sources = template/base.html \
	template/donate.html \
	template/downloads.html \
	template/index.html \
	template/screenshot.html

all: $(HTML) mobile-privacy-policy.html
	./gcompris.py $(VERSION) en "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \

mobile-privacy-policy.html: template/mobile-privacy-policy.html
	cp $< $@

index-%.html: $(sources)
	lang=`echo $@ | sed 's/index-\([^.]*\).html/\1/g'`; \
	./gcompris.py $(VERSION) $$lang "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \


#
# Run it to update the translation. This requires the .po from the -qt version.
update:
	linguas="$(ALL_LINGUAS)"; \
	python2 l10n-fetch-po-files.py "$(ALL_LINGUAS)"; \
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
	  cat $(GCOMPRIS_DIR)/po/gcompris_$$lang.po locale/tempfile | grep -v "^#~" > locale/$$lang/LC_MESSAGES/gcompris.po; \
	  rm -f locale/tempfile; \
	  sed '/^msgctxt "ActivityInfo|"/ d' < locale/$$lang/LC_MESSAGES/gcompris.po > locale/$$lang/LC_MESSAGES/gcompris_tmp.po; \
	  sed '/^msgctxt "DialogHelp/ d' < locale/$$lang/LC_MESSAGES/gcompris_tmp.po > locale/$$lang/LC_MESSAGES/gcompris_tmp2.po; \
	  msguniq --use-first locale/$$lang/LC_MESSAGES/gcompris_tmp2.po -o locale/$$lang/LC_MESSAGES/gcompris.po; \
	  rm -f locale/tempfile locale/$$lang/LC_MESSAGES/gcompris_tmp.po locale/$$lang/LC_MESSAGES/gcompris_tmp2.po; \
	  msgfmt --use-fuzzy locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
	  python3 tools/convertPoToNews.py $$lang locale/$$lang.po; \
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
	rsync -az --copy-unsafe-links --exclude .git --exclude .htaccess --exclude .rcc --exclude template . maintener@gcompris.net:/var/www/

clean:
	rm -Rf *.html feed-*.xml *.pyc locale/*
