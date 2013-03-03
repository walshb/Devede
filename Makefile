.PHONY: all sync test mago

all:

sync:
	MYDIR=`/bin/pwd`; rsync -auvz --exclude '.git/' habanero:src/Devede_blaptop/ $$MYDIR/; rsync -auvz --exclude '.git/' $$MYDIR/ habanero:src/Devede_blaptop/

test:
	./run_conv.sh test

mago:
	export PATH=`/bin/pwd`:$$PATH; export PYTHONPATH=`readlink -f .`:`readlink -f ../ldtp2`; python -m mago.core --pdb tests/mago/test_simple.py
