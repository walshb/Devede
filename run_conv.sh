#!/bin/sh

set -eux

NAME=$1

MYDIR=$(dirname $(readlink -f "$0"))
cd $MYDIR

[ -f ${NAME}.devede2 ] || exit 1

case "`hostname`" in
    ben-laptop*)
        rsync -auvz --exclude '.*' habanero:src/Devede_blaptop/ $MYDIR/
        rsync -auvz --exclude '.*' $MYDIR/ habanero:src/Devede_blaptop/
        ssh habanero "PS1=x . .bashrc; cd src/Devede_blaptop; ./run_conv.sh $NAME"
        exit 0
        ;;
esac

unset DISPLAY
export DISPLAY

echo 'running...' >&2
nohup ./devede_cli.py ${NAME}.devede2 </dev/null >/tmp/${NAME}.log 2>&1 &
echo '...running in background' >&2
