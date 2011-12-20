#!/bin/sh

set -eux

NAME=$1

MYDIR=$(dirname $(readlink -f "$0"))
cd $MYDIR

[ -f ${NAME}.devede2 ] || exit 1

case "`hostname`" in
    ben-laptop*)
        rsync -auvz --exclude '.git/' habanero:src/Devede_blaptop/ $MYDIR/
        rsync -auvz --exclude '.git/' $MYDIR/ habanero:src/Devede_blaptop/
        ssh habanero "PS1=x . .bashrc; cd src/Devede_blaptop; ./run_conv.sh $NAME"
        exit 0
        ;;
esac

unset DISPLAY
export DISPLAY

nohup ./devede_cli.py ${NAME}.devede2 </dev/null >/tmp/${NAME}.log 2>&1 &
