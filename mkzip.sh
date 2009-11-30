#!/bin/bash
VER='0.10'
NAME='key-mon'
rm $NAME-$VER.zip
cd ..
zip key-mon/releases/$NAME-$VER.zip key-mon/*.py key-mon/*.kbd key-mon/key-mon key-mon/themes/**/*.svg key-mon/doc/*.rst key-mon/doc/*.txt -x key-mon/setup.py
