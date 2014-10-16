#
# Makefile -- compiling/copying/install/uninstall the module
#

PREFIX = $(setu)

# Program and Data files and directories.
DEST_PROG_DIR = $(PREFIX)/src/sl/merger-
VER = 0.9
CPFR = cp -fr

# make all -- make programs, data, library, documentation, etc.

all:install-src

install-src:
	mkdir -p $(DEST_PROG_DIR)$(VER)
	cp -fr SSF/ tests/ README.md merge.py helperFuncs.py CHANGELOG $(DEST_PROG_DIR)$(VER)
	$(CPFR) merger_run.sh merger.sh $(DEST_PROG_DIR)$(VER)
	cp Makefile.stage2 $(DEST_PROG_DIR)$(VER)/Makefile

# make compile -- Compiles the source code as well as the data
# compile: compile-exec compile-data

# make install -- Install what all needs to be installed, copying the files from the packages tree to systemwide directories.# it installs the engine and the corpus, dictionary, etc.


# remove the module files from sampark
clean:uninstall
uninstall:
	$(MAKE) -C  $(DEST_PROG_DIR)$(VER) clean
	rm -fr $(DEST_PROG_DIR)$(VER) 

.PHONY: all clean install uninstall install-src 

