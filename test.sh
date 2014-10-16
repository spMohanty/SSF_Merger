#!/bin/bash

for k in {1..995}
do
        echo "File Number :: "$k
		python merge.py --ner tests/ltrc/ner/sentence.$k.ner.wx --mwe tests/ltrc/mwe/sentence.$k.mwe.wx --chunker tests/ltrc/shallowParsed/sentence.$k.shallowParse.wx        
		echo "================================================================================================="
done
