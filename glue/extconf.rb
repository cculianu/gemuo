require 'mkmf'
with_cflags('-g -W -Wall -std=gnu99 -Wmissing-prototypes -Wwrite-strings -Wcast-qual -Wfloat-equal -Wshadow -Wpointer-arith -Wbad-function-cast -Wsign-compare -Waggregate-return -Wmissing-declarations -Wmissing-noreturn -Wmissing-format-attribute -Wnested-externs -Winline -Wdisabled-optimization -Wno-long-long -Wundef -pedantic-errors -Werror') do 1 end
create_makefile('gemuo/glue')
