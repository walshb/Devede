.PHONY: all sync run

all:

sync:
	MYDIR=`/bin/pwd`; rsync -auvz --exclude '.git/' habanero:src/Devede_blaptop/ $$MYDIR/; rsync -auvz --exclude '.git/' $$MYDIR/ habanero:src/Devede_blaptop/

run:
	./run_conv.sh test
