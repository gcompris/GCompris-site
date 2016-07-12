#!/bin/bash
#
# Run me to create the midle and small screenshots from the large png files.
# Run me before pushing to gcompris.net is not yet done or if a new screenshot
# was added.

mkdir -p middle
mkdir -p small
for f in large/*.png
do
    png=${f##*/}
    echo "Processing $f"
    convert $f -resize 50% middle/$png
    convert $f -resize 25% small/$png
done
