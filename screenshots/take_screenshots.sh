#!/bin/sh
# A command example I use to create the screenshots.
# Move them in the screenshots directory with the name found
# in their .xml.in menu name field
xwd -name GCompris | convert - -quality 85 -interlace line -resize 50% $1.jpg
#convert -geometry 130x130 -quality 100 $1.jpg $1_small.jpg
