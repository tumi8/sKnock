.PHONY: all

all: test

test: test.c
	gcc -o test -lpython2.7 $<

clean:
	rm -rf test test.o
