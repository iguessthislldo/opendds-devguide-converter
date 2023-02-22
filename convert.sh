set -e

rm -fr dump devguide build
python3 convert.py
# Replace multiple empty lines with just one
find devguide -type f -name '*.rst' -exec sed -i '/^$/N;/^\n$/D' {} \;
sphinx-build -b html . ./build
if [ ! -z "$DDS_ROOT" ]
then
  cp -r devguide/* $DDS_ROOT/docs/devguide
fi
