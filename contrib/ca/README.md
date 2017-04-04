# PKI CA for sKnock

The client certificates used in sKnock need to fit inside a single UDP packet.
For this reason, sKnock restricts the client certificates to use ECC keys
derived from the prime256v1 (X9.62/SECG curve over a 256 bit prime field) curve.

This CA provides useful scripts to generate such ECC keys, certificates, and
CRLs.  All scripts and commands documented here should be run from the directory
where this README file is present.

## To generate the CA (self-signed) certificate:

    openssl ca -config ca_config -selfsign -keyfile private/cakey.pem -keyform PEM -out cacert.pem

## To generate pkcs12 certificate and key bundles:

    openssl pkcs12 -export -out server.pfx -name "sKnock testing server" -password pass:xxxx -inkey private/server -in certs/02.pem -certfile certs/ca.crt

## TODO
in x509v3_config(1) there is a way to include CRL distribution points
information into a certificate.  We should explore it and include it if deemed
fit for use.


