
VERSION = 1.1

ALL_LINGUAS = be br ca ca@valencia de el es et eu fi fr ga gd gl he hi hu id it ko lt mk ml nl nn pl pt pt_BR ro ru sk sl sq sv tr uk zh_CN zh_TW
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
	template/schools.html \
	template/screenshot.html \
	template/screenshots.html \
	template/test.html

i18_sources = template/base.html \
	template/donate.html \
	template/downloads.html \
	template/index.html \
	template/screenshot.html \
	template/schools.html

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
	python3 l10n-fetch-po-files.py "$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  mkdir -p locale/$$lang/LC_MESSAGES; \
	  mv locale/$$lang.po locale/$$lang/LC_MESSAGES/gcompris.po; \
	  msgfmt --use-fuzzy locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
	  python3 tools/convertPoToNews.py $$lang locale/$$lang/LC_MESSAGES/gcompris.po; \
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
