.PHONY: all sync test mago

all:

sync:
	MYDIR=`/bin/pwd`; rsync -auvz --exclude '.git/' habanero:src/Devede_blaptop/ $$MYDIR/; rsync -auvz --exclude '.git/' $$MYDIR/ habanero:src/Devede_blaptop/

test:
	./run_conv.sh test

mago:
	export PATH=`/bin/pwd`:$$HOME/src/mago/bin:$$PATH; export PYTHONPATH=`/bin/pwd`:$$HOME/src/mago:$$HOME/src/ldtp2; mago --pdb tests/mago/test_simple.py
