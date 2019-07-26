#! /usr/bin/python3
import sys
import csv
import os

def write_matrix_to_c_ary( fname ):
    f = open( fname )
    rdr = csv.reader( f )
    data = [ x for x in rdr ]
    name = fname.split(".")[0]
    f_out = open( name + ".h", "w" )
    f_out.write( "short %s[%d] = { " % ( name, len(data)*len(data[0]) ) )
    for i in range( len(data[0]) ):
        f_out.write( ", ".join( [ data[j][i] for j in range(len(data)) ] ) )
        if i < len(data) - 1:
            f_out.write( ",\n" )
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

def write_bn_relu_to_c( bn_vars_fname, r_shift, bn_relu_out ):
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
    function = "short * %s( const short in[%d], short out[%d] )" % ( func_name, n_vars, n_vars )
    f_out_c.write( function + " {\n" )
    f_out_h.write( function + ";\n" )
    f_out_h.close()
    for i in range( n_vars ):
        out_n = "out[%d]" % i
        in_n = "in[%d]" % i
        f_out_c.write( "%s = ((short)(((short)%d)*%s))+((short)%d)) >> %d;\n" % ( out_n, a[i], in_n, b[i], r_shift ) )
        f_out_c.write( "%s = %s * ( %s > 0 );\n" % ( out_n, out_n, out_n ) )
    f_out_c.write( "return out;\n}\n" )
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
    function = "short * %s( const short in[%d], short out[%d] )" % (func_name, no_in, no_out)
    f_out_c.write( function + " {\n" )
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
