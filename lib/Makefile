.PHONY: all

all: test lknock

lknock: knock.c
	gcc -c -fPIC -Wall -o knock.o knock.c
	gcc -shared -Wall -Wl,-soname,libknock.so.0 -o libknock.so.0.0.0 -lpython2.7 knock.o

test: test.c
	gcc -g -O0 -o test -lpython2.7 $<

clean:
	rm -rf test test.o
	rm -rf knock.o libknock.so*
