SSF Merger
==========

=How to run

-Usage :
```bash
usage: merge.py [-h] -n NER -m MWE -c CHUNKER
```

```bash
python merge.py --ner test_data/ltrc/ner/sentence.957.ner.wx --mwe test_data/ltrc/mwe/sentence.957.mwe.wx --chunker test_data/ltrc/shallowParsed/sentence.957.shallowParse.wx
```
=Test
```bash
bash test.sh
```

Note :: The Input SSF Files should contain only 1 sentence for now, and the contents of the target ssf file is printed to STDOUT
