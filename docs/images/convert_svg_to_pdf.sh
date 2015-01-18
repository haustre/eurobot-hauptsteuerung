#!/bin/bash
# This script converts all svg images to pdf images.
# It is used because latex doesnt support svg.
# Usage:
#   cd docs/images
#   ./convert_svg_to_pdf.sh

for i in ./*.svg; do
  inkscape --without-gui --export-pdf="$(basename $i .svg).pdf" $i
done


#for i in $@; do
#  inkscape --without-gui --export-png="$(basename $i .svg).png" $i
#done
