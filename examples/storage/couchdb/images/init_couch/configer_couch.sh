#!/usr/bin/env bash

fqdn=$(hostname --fqdn)

cp /core-config/default.ini $INSTALL_LOCATION/etc/default.ini
cp /core-config/local.ini $INSTALL_LOCATION/etc/local.ini
cp /core-config/vm.args $INSTALL_LOCATION/etc/vm.args
mkdir $INSTALL_LOCATION/etc/local.d
mkdir $INSTALL_LOCATION/etc/default.d
sed -i $INSTALL_LOCATION/etc/vm.args -e "s/^\-name db/\-name db@$fqdn/"
