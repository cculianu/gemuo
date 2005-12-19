RUBY = /usr/bin/ruby

all: glue/uoglue.so

clean:
	rm -f glue/Makefile glue/*.{o,so}

glue/Makefile: glue/extconf.rb
	cd glue && $(RUBY) extconf.rb

glue/uoglue.so: glue/Makefile
	$(MAKE) -C glue
