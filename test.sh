#!/bin/bash

#!/bin/bash

for k in {1..995}
do
        echo "File Number :: "$k
        python merge.py test_data/ltrc/ner/sentence.$k.ner.wx test_data/ltrc/mwe/sentence.$k.mwe.wx test_data/ltrc/shallowParsed/sentence.$k.shallowParse.wx
        echo "================================================================================================="
done
