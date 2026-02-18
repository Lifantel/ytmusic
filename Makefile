empty:

.PHONY: install

PREFIX?=/usr/local
DESTDIR?=$(PREFIX)/bin

install:
	install -m 755 ./ytmusic.py $(DESTDIR)/ytmusic
