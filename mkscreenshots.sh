PROG='src/keymon/key_mon.py'
# $PROG --screenshot KEY_EMPTY
# mv screenshot.png docs/screenshot-blank.png
# $PROG --screenshot KEY_A,KEY_LEFTCTRL,KEY_LEFTALT,KEY_LEFTSHIFT
# mv screenshot.png docs/screenshot.png
# $PROG --smaller --screenshot KEY_A,KEY_LEFTCTRL,KEY_LEFTALT,KEY_LEFTSHIFT
# mv screenshot.png docs/screenshot-smaller.png
# $PROG --larger --screenshot KEY_A,KEY_LEFTCTRL,KEY_LEFTALT,KEY_LEFTSHIFT
# mv screenshot.png docs/screenshot-larger.png
# $PROG --theme apple --screenshot KEY_A,KEY_LEFTCTRL,KEY_LEFTALT,KEY_LEFTSHIFT
# mv screenshot.png docs/screenshot-apple.png
$PROG --nomouse --scale 2.0 --meta --screenshot KEY_A,KEY_LEFTCTRL,KEY_LEFTALT,KEY_LEFTSHIFT,KEY_LEFTMETA
mv screenshot.png docs/2x-no-mouse-meta.png
