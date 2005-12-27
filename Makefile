RUBY = /usr/bin/ruby

all: gemuo/glue.so

clean:
	rm -f glue/Makefile glue/*.{o,so}

glue/Makefile: glue/extconf.rb
	cd glue && $(RUBY) extconf.rb

glue/glue.so: glue/Makefile
	$(MAKE) -C glue

gemuo/glue.so: glue/glue.so
	cp -a $< $@
