LIBDIR = $(DESTDIR)/usr/lib/pamfingerprint
BINDIR = $(DESTDIR)/usr/bin

clean:
	rm -f *.py[co] */*.py[co]

install:
	mkdir -p $(LIBDIR)
	cp -r src/etc/ $(DESTDIR)/
	cp -r src/lib/ $(DESTDIR)/
	cp -r src/usr/ $(DESTDIR)/

uninstall:
	rm -rf $(LIBDIR)
	rm -f $(DESTDIR)/usr/share/pam-configs/fingerprint
	rm -f $(BINDIR)/pamfingerprint-check
	rm -f $(BINDIR)/pamfingerprint-conf
	rm -f $(DESTDIR)/lib/security/pam_fingerprint.py
	rm -f $(DESTDIR)/etc/bash_completion.d/pamfingerprint
	rm -f $(DESTDIR)/etc/pamfingerprint.conf
