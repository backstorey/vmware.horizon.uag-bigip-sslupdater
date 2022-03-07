#!/bin/bash

openssl pkcs12 -in $1 -nokeys -out ./cert.pem
openssl pkcs12 -in $1 -nodes -nocerts -out ./key.pem
openssl rsa -in ./key.pem -check -out ./key-rsa.pem
openssl x509 -noout -fingerprint -sha1 -inform pem -in ./cert.pem > ./thumbprint.txt

awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' ./cert.pem > ./oneline-cert.pem
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' ./key-rsa.pem > ./oneline-key-rsa.pem

python3 ./update-ssl-controlscript.py

rm -f *.pem thumbprint.txt