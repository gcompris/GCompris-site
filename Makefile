
VERSION = 3.0

# Don't forget to also update index.php and gcompris.py when updating this list
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
	PYTHONPATH="./$(GCOMPRIS_DIR)/tools/python" ./gcompris.py $(VERSION) en "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \

mobile-privacy-policy.html: template/mobile-privacy-policy.html
	cp $< $@

index-%.html: $(sources)
	lang=`echo $@ | sed 's/index-\([^.]*\).html/\1/g'`; \
	PYTHONPATH="./$(GCOMPRIS_DIR)/tools/python" ./gcompris.py $(VERSION) $$lang "$(ALL_LINGUAS)" $(GCOMPRIS_DIR); \

#
# Run it to update the translation.
# 1) Download the corresponding GCompris source version if not already present.
# 2) We convert the po files from the GCompris source folder to .qm files to be read by PyQt (to get the ActivityInfo.qml translated).
# 3) The second for loop is to retrieve the gcompris-net po files and convert them to .mo files to be used by Jinja2.
update: downloadGComprisSrc
	linguas="$(ALL_LINGUAS)"; \
	for lang in $$linguas; do \
	  translationFolder="po/$$lang/LC_MESSAGES"; \
	  outTsFile="$$translationFolder/gcompris_qt.ts"; \
	  outQmFile="$$translationFolder/gcompris_qt.qm"; \
	  mkdir -p $$translationFolder; \
	  if [ -f "$(GCOMPRIS_DIR)/poqm/$$lang/gcompris_qt.po" ]; then \
		  msgattrib --no-obsolete $(GCOMPRIS_DIR)/poqm/$$lang/gcompris_qt.po -o $$outTsFile; \
		  lconvert -if po -of ts -i $$outTsFile -o $$outTsFile; \
		  lrelease -compress -nounfinished $$outTsFile -qm $$outQmFile; \
	  fi; \
	done; \
	for lang in $$linguas; do \
	  if [ -f po/$$lang/gcompris-net.po ]; then \
		cp po/$$lang/gcompris-net.po po/$$lang/LC_MESSAGES/gcompris.po; \
		msgfmt --use-fuzzy po/$$lang/LC_MESSAGES/gcompris.po -o po/$$lang/LC_MESSAGES/gcompris.mo; \
		python3 tools/convertPoToNews.py $$lang po/$$lang/LC_MESSAGES/gcompris.po; \
	fi; \
	done;
#
# Run this when new strings are added in the templates
extract: $(i18_sources)
	pybabel extract -F babel.cfg -o po/messages.pot ./
	if test $(shell git diff po/messages.pot | grep "^+[^+]" | wc -l) -eq 1; then \
	  git checkout po/messages.pot; \
	  touch po/messages.pot; \
	fi

online:
	rsync -az --copy-unsafe-links --exclude "*.py" --exclude ".git" --exclude ".gitignore" --exclude ".directory" --exclude ".htaccess" --exclude ".rcc" --exclude ".emacs.d" --exclude "__pycache__" --exclude "babel.cfg" --exclude "Makefile" --exclude "Messages.sh" --exclude "po" --exclude "tools" --exclude "newsTemplate" --exclude "template" --exclude "gcompris-qt-*" --exclude "fonts" . maintener@gcompris.net:/var/www/

clean:
	rm -Rf *.html feed-*.xml *.pyc news/*.html po/*/LC_MESSAGES/
