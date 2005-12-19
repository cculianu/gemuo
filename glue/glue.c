#include <ruby.h>

#include "packets.h"
#include "compression.h"
#include "buffer.h"

struct decompress {
    struct uo_decompression backend;
    struct buffer *input, *output;
};

static VALUE mUO, mUOPacket, cDecompress/*, cPacketReader*/;

static void decompress_free(void *p) {
    struct decompress *decompress = p;

    if (decompress->input != NULL)
        buffer_delete(decompress->input);

    if (decompress->output != NULL)
        buffer_delete(decompress->output);
}

static VALUE decompress_new(VALUE class, VALUE io) {
    VALUE self;
    struct decompress *decompress;
    VALUE argv[1];

    self = Data_Make_Struct(class, struct decompress,
                            NULL, decompress_free, decompress);

    uo_decompression_init(&decompress->backend);
    decompress->input = buffer_new(4096);
    decompress->output = buffer_new(65536);

    if (decompress->input == NULL || decompress->output == NULL)
        rb_raise(rb_eNoMemError, NULL);

    argv[0] = io;
    rb_obj_call_init(self, 1, argv);

    return self;
}

static VALUE decompress_initialize(VALUE self, VALUE io) {
    rb_iv_set(self, "@io", io);
    return self;
}

static VALUE buffer_shift_ruby(struct buffer *b, void *p, size_t length) {
    VALUE ret;

    ret = rb_str_new((const char*)p, length);
    buffer_shift(b, length);

    return ret;
}

static VALUE decompress_read(VALUE self, VALUE _length) {
    struct decompress *decompress;
    void *p, *r;
    int length;
    size_t p_length, r_length;
    VALUE result;
    long s_length;
    ssize_t nbytes;

    length = NUM2INT(_length);
    if (length <= 0)
        return rb_str_new2("");

    Data_Get_Struct(self, struct decompress, decompress);

    for (;;) {
        /* already enough in output buffer? */
        p = buffer_peek(decompress->output, &p_length);
        if (p == NULL)
            p_length = 0;
        if (p_length >= (size_t)length)
            return buffer_shift_ruby(decompress->output, p, (size_t)length);

        /* read from @io to input buffer */
        buffer_commit(decompress->input);
        r_length = buffer_free(decompress->input);
        if (r_length == 0)
            rb_raise(rb_eNoMemError, "buffer too small");

        result = rb_funcall(rb_iv_get(self, "@io"), rb_intern("sysread"), 1,
                            INT2FIX(r_length));

        r = rb_str2cstr(result, &s_length);
        if (s_length == 0)
            return buffer_shift_ruby(decompress->output, p, p_length);

        memcpy(buffer_tail(decompress->input), r, s_length);
        buffer_expand(decompress->input, s_length);

        /* decompress */
        r = buffer_peek(decompress->input, &r_length);
        if (r == NULL)
            return buffer_shift_ruby(decompress->output, p, p_length);

        buffer_commit(decompress->output);
        nbytes = uo_decompress(&decompress->backend,
                               buffer_tail(decompress->output),
                               buffer_free(decompress->output),
                               r, r_length);
        if (nbytes < 0)
            rb_raise(rb_eException, "decompression failed");

        buffer_shift(decompress->input, r_length);
        buffer_expand(decompress->output, nbytes);
    }
}

static VALUE packet_length(VALUE self, VALUE _cmd) {
    int cmd = NUM2INT(_cmd);

    (void)self;

    if (cmd < 0 || cmd >= 0x100)
        return 0; /* XXX raise? */

    return INT2FIX(packet_lengths[cmd]);
}

/*
static VALUE preader_initialize(VALUE self, VALUE io) {
    rb_iv_set(self, "@io", io);
    return self;
}

static VALUE preader_read(VALUE self) {
    VALUE io = rb_iv_get(self, "@io");
    VALUE data;
    data = rb_funcall(io, rb_intern("readchar"), 0);
    return self;
}
*/

void Init_uoclient(void);
void Init_uoclient(void) {
    mUO = rb_define_module("UO");

    cDecompress = rb_define_class_under(mUO, "Decompress", rb_cObject);
    rb_define_singleton_method(cDecompress, "new", decompress_new, 1);
    rb_define_method(cDecompress, "initialize", decompress_initialize, 1);
    rb_define_method(cDecompress, "sysread", decompress_read, 1);

    mUOPacket = rb_define_module("UO::Packet");

    rb_define_module_function(mUO, "packet_length", packet_length, 1);

    /*
    cPacketReader = rb_define_class_under(mUOPacket, "Reader", rb_cObject);
    rb_define_method(cPacketReader, "initialize", preader_initialize, 1);
    rb_define_method(cPacketReader, "read", preader_read, 1);
    */
}
