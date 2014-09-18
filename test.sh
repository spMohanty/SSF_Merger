#!/bin/bash

for k in {1..995}
do
        echo "File Number :: "$k
		python merge.py --ner test_data/ltrc/ner/sentence.$k.ner.wx --mwe test_data/ltrc/mwe/sentence.$k.mwe.wx --chunker test_data/ltrc/shallowParsed/sentence.$k.shallowParse.wx        
		echo "================================================================================================="
done
