
VERSION = 2.4

ALL_LINGUAS = be br ca ca@valencia de el es et eu fi fr gd gl he hu id it ko lt mk ml nl nn pl pt pt_BR ro ru sk sl sq sv tr uk zh_CN zh_TW
#ALL_LINGUAS = fr

GCOMPRIS_DIR="gcompris-qt-$(VERSION)"

HTML := $(ALL_LINGUAS:%=index-%.html)

sources = \
	gcompris.py \
	template/base.html \
	template/christmas.html \
	template/donate.html \
	template/downloads.html \
	template/index.html \
	template/news.html \
	template/newsall.html \
	template/onenews.html \
	template/schools.html \
	template/screenshot.html \
	template/screenshots.html \
	template/singlenews.html

i18_sources = template/base.html \
	template/donate.html \
	template/downloads.html \
	template/index.html \
	template/screenshot.html \
	template/schools.html

downloadGComprisSrc:
	if [ ! -d "$(GCOMPRIS_DIR)" ]; then \
		wget "https://gcompris.net/download/qt/src/gcompris-qt-$(VERSION).tar.xz"; \
		tar -xf "gcompris-qt-$(VERSION).tar.xz"; \
		rm -f "gcompris-qt-$(VERSION).tar.xz"; \
	fi;

all: $(HTML) mobile-privacy-policy.html
	./gcompris.py $(VERSION) en "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \

mobile-privacy-policy.html: template/mobile-privacy-policy.html
	cp $< $@

index-%.html: $(sources)
	lang=`echo $@ | sed 's/index-\([^.]*\).html/\1/g'`; \
	./gcompris.py $(VERSION) $$lang "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \

#
# Run it to update the translation.
# 1) Download the corresponding GCompris source version if not already present.
# 2) We convert the po files from the GCompris source folder to .qm files to be read by PyQt (to get the ActivityInfo.qml translated).
# 3) The second for loop is to retrieve the gcompris-net po files and convert them to .mo files to be used by Jinja2.
update: downloadGComprisSrc
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  translationFolder="locale/$$lang/LC_MESSAGES"; \
	  outTsFile="$$translationFolder/gcompris_qt.ts"; \
	  outQmFile="$$translationFolder/gcompris_qt.qm"; \
	  mkdir -p $$translationFolder; \
	  if [ -f "$(GCOMPRIS_DIR)/po/gcompris_$$lang.po" ]; then \
		  msgattrib --no-obsolete $(GCOMPRIS_DIR)/po/gcompris_$$lang.po -o $$outTsFile; \
		  lconvert -if po -of ts -i $$outTsFile -o $$outTsFile; \
		  lrelease -compress -nounfinished $$outTsFile -qm $$outQmFile; \
	  fi; \
	done; \
	python3 l10n-fetch-po-files.py "$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  if [ -f locale/$$lang.po ]; then \
		mv locale/$$lang.po locale/$$lang/LC_MESSAGES/gcompris.po; \
		msgfmt --use-fuzzy locale/$$lang/LC_MESSAGES/gcompris.po -o locale/$$lang/LC_MESSAGES/gcompris.mo; \
		python3 tools/convertPoToNews.py $$lang locale/$$lang/LC_MESSAGES/gcompris.po; \
	fi; \
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
	rsync -az --copy-unsafe-links --exclude "*.py" --exclude ".git" --exclude ".gitignore" --exclude ".directory" --exclude ".htaccess" --exclude ".rcc" --exclude ".emacs.d" --exclude "__pycache__" --exclude "babel.cfg" --exclude "Makefile" --exclude "Messages.sh" --exclude "locale" --exclude "tools" --exclude "newsTemplate" --exclude "template" --exclude "gcompris-qt-*" . maintener@gcompris.net:/var/www/

clean:
	rm -Rf *.html feed-*.xml *.pyc locale/* news/*.html
