#!/bin/sh
#
# $Header$

set -eux

PREFIX=$HOME/opt/devede-head

inst_devede() {
    rm -rf $PREFIX

    TMPDIR=/tmp/devede_tmp.$$
    TMPDIR2=/tmp/devede_tmp2.$$
    mkdir -p $TMPDIR
    mkdir -p $TMPDIR2
    cp -rv -T $HOME/src/Devede $TMPDIR
    cd $TMPDIR
    for FILE in `find . -name '.git' -prune -o -type f -print`
    do
        sed -i -e "s|/usr/share|$PREFIX/share|g" \
            -e "s|/usr/local/share|$PREFIX/share|g" \
            -e "s|/usr/lib/devede|$PREFIX/lib/devede|g" \
            -e "s|/usr/local/lib/devede|$PREFIX/lib/devede|g" \
        $FILE
    done

    cd $TMPDIR/pixmaps
    for FILE in *.mpg
    do
        echo $FILE >&2
        case "$FILE" in
        *pal*)  TARGET=pal-dvd
                ;;
        *ntsc*) TARGET=ntsc-dvd
                ;;
        esac
        ffmpeg -i $FILE -target $TARGET -an -copyts $TMPDIR2/$FILE
        mv $TMPDIR2/$FILE $FILE
    done

    cd $TMPDIR
    ./install.sh --prefix=$PREFIX
}

inst_devede
