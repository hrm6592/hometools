#!/bin/bash

pushd /root/cert

# File check
rm -f *.pem
[ ! -f certificate_authority_template.info ] && exit 1
[ ! -f admin_desktop_client_template.info ] && exit 1
[ ! -f host1_client_template.info ] && exit 1
[ ! -f host1_server_template.info ] && exit 1

# CA certificate
(umask 277 && certtool --generate-privkey > certificate_authority_key.pem)
certtool \
  --generate-self-signed \
  --template certificate_authority_template.info \
  --load-privkey certificate_authority_key.pem \
  --outfile certificate_authority_certificate.pem
cp -pf certificate_authority_certificate.pem /etc/pki/CA/cacert.pem
chmod 0444 /etc/pki/CA/cacert.pem
chown root:root /etc/pki/CA/cacert.pem

# Server certificate for Host1
(umask 277 && certtool --generate-privkey > host1_server_key.pem)
certtool \
  --generate-certificate \
  --template host1_server_template.info \
  --load-privkey host1_server_key.pem \
  --load-ca-certificate certificate_authority_certificate.pem \
  --load-ca-privkey certificate_authority_key.pem \
  --outfile host1_server_certificate.pem
chmod 755 /etc/pki/libvirt
chmod 750 /etc/pki/libvirt/private
rm /etc/pki/libvirt/*.pem
cp -pf host1_server_certificate.pem /etc/pki/libvirt/servercert.pem
rm /etc/pki/libvirt/private/*.pem
cp -pf host1_server_key.pem /etc/pki/libvirt/private/serverkey.pem
chgrp qemu /etc/pki/libvirt \
           /etc/pki/libvirt/servercert.pem \
           /etc/pki/libvirt/private \
           /etc/pki/libvirt/private/serverkey.pem
chmod 440 /etc/pki/libvirt/servercert.pem \
          /etc/pki/libvirt/private/serverkey.pem

# Client certificate for Host1
(umask 277 && certtool --generate-privkey > host1_client_key.pem)
certtool \
  --generate-certificate \
  --template host1_client_template.info \
  --load-privkey host1_client_key.pem \
  --load-ca-certificate certificate_authority_certificate.pem \
  --load-ca-privkey certificate_authority_key.pem \
  --outfile host1_client_certificate.pem
cp -pf host1_client_certificate.pem /etc/pki/libvirt/clientcert.pem
cp -pf host1_client_key.pem /etc/pki/libvirt/private/clientkey.pem
chmod 400 /etc/pki/libvirt/clientcert.pem \
          /etc/pki/libvirt/private/clientkey.pem

# Client certificate for Adiministoration host.
(umask 277 && certtool --generate-privkey > admin_desktop_client_key.pem)
certtool \
  --generate-certificate \
  --template admin_desktop_client_template.info \
  --load-privkey admin_desktop_client_key.pem \
  --load-ca-certificate certificate_authority_certificate.pem \
  --load-ca-privkey certificate_authority_key.pem \
  --outfile admin_desktop_client_certificate.pem
popd
