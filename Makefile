empty:

.PHONY: install

PREFIX?=/usr/local

install:
	install -m 755 ./ytmusic.py $(PREFIX)/bin/ytmusic
