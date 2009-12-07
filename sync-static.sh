#!/bin/sh
#
# Ideally this should be a part of puppy configurable via puppy.yaml.

cp -R app/public/ $HOME/DropBoxes/cmc/Dropbox/Public/public/
rsync -avc app/public/ yesudeep@assets.cuttingmasalachai.com:/var/www/assets.cuttingmasalachai.com/
