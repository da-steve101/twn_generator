#! /usr/bin/python3

import csv
from . import add_ops

def get_name( idx, no_inputs, BW ):
    if idx < 0: # if unused then is 0
        return str(BW) + "'h0"
    if idx < no_inputs:
        return "in[" + str(idx) + "]"
    return "tree_" + str(idx - no_inputs)

def get_max_d( depths ):
    return max( [ depths[i] for i in depths ] )

def create_vld_and_reset( max_depth ):
    assert max_depth >= 1, "Must have atleast 1 stage"
    module_vld_rst = "reg [" + str( max_depth - 1 ) + ":0] vld_reg = 0;\n"
    module_vld_rst += "wire [" + str( max_depth - 1 ) + ":0] resets;\n"
    if max_depth >= 2:
        module_vld_rst += "reg [" + str( max_depth - 2 ) + ":0] rst_reg;\n"
        module_vld_rst += "assign resets = { rst_reg, reset };\n"
    else:
        module_vld_rst += "assign resets[0] = reset;\n"
    module_vld_rst += "assign vld_out = vld_reg[" + str(max_depth - 1) + "];\n"
    module_vld_rst += "always @( posedge clock ) begin\n"
    if max_depth >= 2:
        module_vld_rst += "vld_reg <= { vld_reg[" + str( max_depth - 2) + ":0], vld_in };\n"
    else:
        module_vld_rst += "vld_reg[0] <= vld_in;\n"
    if max_depth >= 2:
        module_vld_rst += "rst_reg <= resets[" + str(max_depth-2) + ":0];\n"
    module_vld_rst += "end\n"
    return module_vld_rst

def set_outputs( depths, output_idxs, bws, BW, no_inputs, signed_ext = True ):
    # make sure all the outputs match the correct depth
    max_depth = get_max_d( depths )
    declarations = []
    computations = []
    for idx, oi in enumerate( output_idxs ):
        delay_reg = max_depth - depths[oi]
        padded_out = get_name( oi, no_inputs, BW )
        if signed_ext and oi != -1 and bws[oi] < BW:
            padded_out = "{ {" + str( BW-bws[oi] ) + "{" + padded_out + "[" + str( bws[oi]-1 ) + "]}}," + padded_out + "}"
        if delay_reg == 0 or get_name( oi, no_inputs, BW ) == str(BW) + "'h0":
            declarations += [ "assign out[" + str(idx) + "] = " + padded_out + ";" ]
        elif delay_reg == 1:
            declarations += [ "reg [" + str(BW-1) + ":0] out_" + str(idx) + ";" ]
            declarations += [ "assign out[" + str(idx) + "] = out_" + str(idx) + ";" ]
            computations += [ "out_" + str(idx) + " <= " + padded_out + ";" ]
        else:
            declarations += [ "reg [" + str(delay_reg-1) + ":0][" + str(BW-1) + ":0] out_" + str(idx) + ";" ]
            declarations += [ "assign out[" + str(idx) + "] = out_" + str(idx) + "[" + str(delay_reg - 1) + "];" ]
            computations += [ "out_" + str(idx) + " <= { out_" + str(idx) + "[" + str( delay_reg - 2 ) + ":0], " + padded_out + "};" ]
    output_txt = "\n".join( declarations )
    output_txt += "\nalways @( posedge clock ) begin\n"
    output_txt += "\n".join( computations )
    output_txt += "\nend\n"
    return output_txt

def SMM_generate( fname_ops, module_name, BW_in, BW_out, create_op ):
    f = open( fname_ops )
    rdr = csv.reader( f )
    ops = [ [ int(x) for x in y ] for y in rdr ]
    output_idxs = ops[0]
    ops = ops[1:]
    no_inputs = ops[0][0]
    module_header = "module " + module_name + """ (
input clock,
input reset,
input vld_in,
input [""" + str( no_inputs - 1) + ":0][" + str(BW_in-1) + """:0] in,
output vld_out,
output [""" + str( len(output_idxs) - 1) + ":0][" + str(BW_out-1) + """:0] out
);
"""
    depths = {}
    bws = {}
    depths[-1] = 0
    bws[-1] = BW_out
    for i in range( no_inputs ):
        depths[i] = 0
        bws[i] = BW_in
    module_body = ""
    declarations = []
    computations = []
    # implement all the ops
    for op in ops:
        stage_reset = "resets[" + str(depths[op[1]]) + "]"
        names = [ get_name( idx, no_inputs, BW_out ) for idx in op[:4] ]
        module_txt, op_BW = create_op( names, op[4], op[5:], BW_in, BW_out, "op_" + str(op[0]), stage_reset, depths[op[1]] )
        module_body += module_txt
        bws[op[0]] = op_BW
        if op[2] != -1:
            assert depths[op[1]] == depths[op[2]], "Depths mismatch, invalid tree in op = " + str( op )
        depths[op[0]] = depths[op[1]] + 1
    max_depth = get_max_d( depths )
    module_header += create_vld_and_reset( max_depth )
    module_body += set_outputs( depths, output_idxs, bws, BW_out, no_inputs )
    module_body += "endmodule\n"
    return module_header + module_body
