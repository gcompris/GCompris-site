#!/bin/bash
#
# Run me to create the midle and small screenshots from the large png files.
# Run me before pushing to gcompris.net is not yet done or if a new screenshot
# was added.

# Requires optipng (apt install optipng)
# and pngquant (to compile if not packaged https://pngquant.org/)

mkdir -p middle
mkdir -p small
for f in large/*.png
do
    png=${f##*/}

    if [ ! -f middle/$png ]
    then
        echo "Processing middle $f"
        convert $f -resize 50% middle/$png
        pngquant -f --quality 50-100 --output middle/$png middle/$png
        optipng middle/$png
    fi

    if [ ! -f small/$png ]
    then
        echo "Processing small $f"
        convert $f -resize 25% small/$png
        pngquant -f --quality 50-100 --output small/$png small/$png
        optipng small/$png

        # Also optimize the new source file ; now commented as new files as been optimized already
        # optipng large/$png
    fi
done
