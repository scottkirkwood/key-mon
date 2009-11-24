#!/bin/bash
VER='0.3'
NAME='key-mon'
rm $NAME-$VER.zip
cd ..
zip key-mon/$NAME-$VER.zip key-mon/*.py key-mon/svg/*.svg key-mon/doc/*.rst key-mon/doc/*.txt -x key-mon/setup.py
