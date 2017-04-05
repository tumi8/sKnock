SHELL = /bin/sh
NEW_DIRS = certs private csrs certs/server certs/client private/server	\
	private/client csrs/server csrs/client
NEW_FILES = index.txt serial crl_serial
PFX_PASSWORD = portknocking

init: create-fs certs/ca.pem

create-fs: serial crl_serial index.txt
	@for dir in $(NEW_DIRS); do \
	  if [ ! -d "$${dir}" ]; then mkdir -p "$${dir}"; fi \
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

certs/server/%.pem: csrs/server/%.pem private/ca.key
	openssl ca -config configs/client_config -in "$<"\
	  -extensions server_extensions -out "$@"

certs/client/%.pem: csrs/client/%.pem private/ca.key
	openssl ca -config configs/client_config -in "$<"\
	  -extensions client_extensions -out "$@"

certs/%.crt: certs/%.pem
	openssl x509 -inform PEM -in "$<" -outform DER -out "$@"

certs/%.pfx: certs/%.pem certs/%.crt private/%.key
	openssl pkcs12 -export -out "$@" -inkey "private/$*.key" -in "$<"\
	  -certfile certs/ca.pem -password "pass:$(PFX_PASSWORD)"

gen-server-cert: certs/server/$(NAME).pfx
	$(info The server PKCS12 bundle is created at "$<" with\
		password: $(PFX_PASSWORD))
	$(info The server certificate is available at: "certs/server/$(NAME).crt")

gen-client-cert: certs/client/$(NAME).pfx
	$(info The client PKCS12 bundle is created at: "$<" with\
		password: $(PFX_PASSWORD))

clean_no_i_am_not_drunk:
	rm -rf $(NEW_DIRS) $(NEW_FILES)
	rm -rf index.txt{,.old} index.txt.attr{,.old}
	rm -rf serial.old

test:
	@echo "Hello World"

.PHONY: init create-fs gen-server-cert gen-client-cert

.PRECIOUS: private/%.key certs/%.crt csrs/%.pem
