SSF Merger
==========

=Installaion    
   
```bash
export setu=$HOME/sampark #or wherever your sampark root directory is 
env | grep setu #Make sure $setu variable is set 
git clone https://github.com/spMohanty/SSF_Merger
cd SSF_Merger
export version=`git describe --abbrev=0 --tags | sed 's/v//g'`
make
cd $setu/src/sl/merger-$version
make install
```
   
=How to run

-Usage :
```bash
usage: merge.py [-h] -n NER -m MWE -c CHUNKER
```

```bash
python merge.py --ner test_data/ltrc/ner/sentence.826.ner.wx --mwe test_data/ltrc/mwe/sentence.826.mwe.wx --chunker test_data/ltrc/shallowParsed/sentence.826.shallowParse.wx
```
=Test
```bash
bash test.sh
```

Note :: The Input SSF Files should contain only 1 sentence for now, and the contents of the target ssf file is printed to STDOUT   
   
Note :: The merger module DOES NOT expect the individual tokens to be marked by etypes, but it does not mind if they are already marked. The merger module doesnot change the etypes of individual chunks, and in case of a conflict it assigns the etype based on the priority MWE > NER > CHUNKER   
