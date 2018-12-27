
EXEC = mrtfeeder
BIN = ./bin
SRC = ./src

INSTALL = /usr/bin/install -c
INSTALL_PROGRAM = ${INSTALL}
INSTALL_MODE= -m 0755

prefix = /usr/local
exec_prefix = ${prefix}
bindir = ${exec_prefix}/bin

all:
	gcc -g $(SRC)/$(EXEC).c -o $(BIN)/$(EXEC)

clean:
	rm -f $(BIN)/$(EXEC)

install:
	-( mkdir -p $(bindir) )
	$(INSTALL_PROGRAM) $(INSTALL_MODE) $(BIN)/$(EXEC) $(bindir)/$(EXEC)
