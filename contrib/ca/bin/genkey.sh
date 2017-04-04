#!/bin/sh
# Usage: genkey.sh FILE
#   where FILE is the file to store the private key
#
# Generates and writes a private key from prime256v1 curve.  Corresponding
# public key is written to file.pub

openssl ecparam -genkey -name prime256v1 -param_enc named_curve -out $1
openssl ec -in $1 -pubout -out $1.pub
