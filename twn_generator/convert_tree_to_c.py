#! /usr/bin/python3
import sys
import csv
import os

def write_matrix_to_c_ary( fname, extra_str = "" ):
    f = open( fname )
    rdr = csv.reader( f )
    data = [ [ float(y) for y in x ] for x in rdr ]
    dirname = os.path.dirname( fname )
    mod_file = os.path.basename( fname )
    name = mod_file.split(".")[0]
    f_out = open( dirname + "/" + name + ".h", "w" )
    name_u = name.upper()
    f_out.write( "%s\n" % extra_str )
    f_out.write( "#define %s_LEN %s\n" % ( name_u, len(data) ) )
    f_out.write( "#define %s_FILT %s\n" % ( name_u, len(data[0]) ) )
    f_out.write( "const float %s[%s_LEN*%s_FILT] = { " % ( name, name_u, name_u ) )
    for i in range( len(data) ):
        f_out.write( ", ".join( [ str(x) for x in data[i] ] ) )
        if i != len(data) - 1:
            f_out.write( ", " )
    f_out.write( "};\n" )
    f_out.close()

def get_name( op_idx, no_in, prefix = "in" ):
    if int( op_idx ) < 0:
        return ""
    if int( op_idx ) < no_in:
        return prefix + "[" + str(op_idx) + "]"
    return prefix + "_" + str(op_idx)

def op_to_str( op, no_in, prefix = "in" ):
    a_str = get_name( op[1], no_in, prefix )
    b_str = get_name( op[2], no_in, prefix )
    c_str = get_name( op[3], no_in, prefix )
    if a_str == '' or op[0] == -1:
        return ''
    op_str = "short %s = " % get_name( op[0], no_in, prefix )
    if not a_str == '':
        if int( op[4] ) < 4:
            op_str += "-"
        op_str += a_str
    if not b_str == '':
        if int( op[4] ) % 4 < 2:
            op_str += " - "
        else:
            op_str += " + "
        op_str += b_str
    if not c_str == '':
        if int( op[4] ) % 2 < 1:
            op_str += " - "
        else:
            op_str += " + "
        op_str += c_str
    op_str += ";\n"
    return op_str

def write_bn_relu_to_c( bn_vars_fname, r_shift, bn_relu_out, quantize_to = None ):
    f_ops = open( bn_vars_fname )
    rdr = csv.reader( f_ops )
    data = [ [ int(x) for x in y ] for y in rdr ]
    a = data[0]
    b = data[1]
    n_vars = len(data[0])
    func_name = os.path.basename( bn_relu_out )
    f_out_c = open( bn_relu_out + ".c", "w" )
    f_out_h = open( bn_relu_out + ".h", "w" )
    f_out_c.write( "#include \"%s.h\"\n" % func_name )
    function = "short * %s( short in[%s_FILT] )" % ( func_name, func_name.upper() )
    f_out_c.write( function + " {\n" )
    f_out_h.write( "#define %s_FILT %d\n" %( func_name.upper(), n_vars ) )
    f_out_h.write( function + ";\n" )
    f_out_h.close()
    for i in range( n_vars ):
        in_n = "in[%d]" % i
        f_out_c.write( "%s = (short)(((%d*((int)%s))+%d) >> %d);\n" % ( in_n, a[i], in_n, b[i], r_shift ) )
        f_out_c.write( "%s = %s * ( %s > 0 );\n" % ( in_n, in_n, in_n ) )
        if quantize_to is not None:
            shift, max_val = quantize_to
            f_out_c.write( "%s = %s >> %d;\n" % ( in_n, in_n, shift ) )
            f_out_c.write( "%s = %s > %d ? %d : %s;\n" % ( in_n, in_n, max_val, max_val, in_n ) )
    f_out_c.write( "return in;\n}\n" )
    f_out_c.close()
    return

def write_tree_to_c( op_fname, conv_out ):
    f_ops = open( op_fname )
    rdr = csv.reader( f_ops )
    data = [ x for x in rdr ]
    outputs = data[0]
    ops = data[1:]
    no_in = int( ops[0][0] )
    no_out = len(outputs)
    func_name = os.path.basename( conv_out )
    f_out_c = open( conv_out + ".c", "w" )
    f_out_h = open( conv_out + ".h", "w" )
    f_out_c.write( "#include \"%s.h\"\n" % func_name )
    function = "short * %s( const short in[%s_IN], short out[%s_OUT] )" % ( func_name, func_name.upper(), func_name.upper() )
    f_out_c.write( function + " {\n" )
    f_out_h.write( "#define %s_IN %d\n" % (func_name.upper(), no_in) )
    f_out_h.write( "#define %s_OUT %d\n" %( func_name.upper(), no_out) )
    f_out_h.write( function + ";\n" )
    f_out_h.close()
    for op in ops:
        f_out_c.write( op_to_str( op, no_in ) )
    for i, x in enumerate(outputs):
        n = get_name( x, no_in )
        if n == "":
            n = "0"
        f_out_c.write( "out[%s] = %s;\n" % ( i, n ) )
    f_out_c.write( "return out;\n}\n" )
    return
