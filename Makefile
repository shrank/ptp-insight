.PHONY: vuejsfrontend static clean dist
python=python3
VERSION="0.0.2"
BUILD=$(shell date +%Y%m%d%H%M)
NAME=ptp-insight
PKG=${NAME}-${VERSION}-${BUILD}
DPKG_ARCH:=all
DPKG=dpkg-deb


all: static

static:
#	cd frontend && npm run build

dist: release/${PKG}.deb

build/${PKG}: static
	mkdir -p $@/etc/ptp
	mkdir -p $@/usr/share/${NAME}/static
	mkdir -p $@/usr/lib/systemd/system/
	mkdir -p $@/etc/default/
	mkdir -p $@/var/lib/${NAME}
	mkdir -p $@/DEBIAN
	cp src/*.py $@/usr/share/${NAME}/
	cp -r dist/configs/* $@/etc/ptp/
	cp -r frontend/dist/* $@/usr/share/${NAME}/static/
	cp dist/${NAME}.service $@/usr/lib/systemd/system/
	cp dist/${NAME}-web.service $@/usr/lib/systemd/system/
	cp dist/postinst $@/DEBIAN/postinst
	chmod 755 $@/DEBIAN/postinst
	cp dist/dpkg-control $@/DEBIAN/control
	echo Version: ${VERSION}-${BUILD} >> $@/DEBIAN/control
	echo Architecture: ${DPKG_ARCH} >> $@/DEBIAN/control

release/${PKG}.deb: build/${PKG}
	mkdir -p release
	${DPKG} -b $< $@

clean:
	rm -rf build

