#!/bin/bash

echo $1
echo $2
python ssfDiff.py $1 $2
xmldiff tmp/xml1 tmp/xml2