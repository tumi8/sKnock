SHELL = /bin/sh
NEW_DIRS = certs csrs private certs/server certs/client
NEW_FILES = index.txt serial crl_serial
SERVER_NAME = server
PFX_PASSWORD = portknocking

init: create-fs certs/ca.pem

create-fs: serial crl_serial index.txt
	@for dir in ${NEW_DIRS}; do \
	  if [ ! -d "$${dir}" ]; then mkdir "$${dir}"; fi \
	done

index.txt:
	@touch index.txt index.txt.attr

serial:
	echo 01 > serial

crl_serial:
	echo 00 > crl_serial

certs/ca.pem: private/ca.key
	openssl req -config configs/ca_config -x509 -key private/ca.key\
	   -set_serial 0 -out certs/ca.pem 2>&1

private/%.key:
	openssl ecparam -genkey -name prime256v1 -param_enc named_curve\
	   -out "$@"

csrs/%.pem:  private/%.key
	openssl req -config configs/client_config -new\
	  -key "$<" -out "$@"

certs/server/%.pem: csrs/%.pem private/ca.key
	openssl ca -config configs/client_config -in "$<"\
	  -extensions server_extensions -out "$@"

certs/server/%.crt: certs/server/%.pem
	openssl x509 -inform PEM -in "$<" -outform DER -out "$@"

certs/server/%.pfx: certs/server/%.pem certs/server/%.crt private/%.key
	openssl pkcs12 -export -out "$@" -inkey "private/$*.key" -in "$<"\
	  -certfile certs/ca.pem -password "pass:${PFX_PASSWORD}"

gen-server-cert: certs/server/${SERVER_NAME}.pfx

clean_no_i_am_not_drunk:
	rm -rf ${NEW_DIRS} ${NEW_FILES}
	rm -rf index.txt{,.old} index.txt.attr{,.old}

test:
	@echo "Hello World"

.PHONY: init create-fs generate-ca-certificate generate-ca-keys
