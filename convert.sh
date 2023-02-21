set -e

rm -fr dump devguide build
python3 convert.py
sphinx-build -b html . ./build
if [ ! -z "$DDS_ROOT" ]
then
  cp -r devguide/* $DDS_ROOT/docs/devguide
fi
