#! /usr/bin/python3

import argparse
import twn_generator as twn

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--matrix_fname", type = str, required = True,
                         help="The csv file with values 1,0 or -1")
    parser.add_argument( "--cse_fname", type = str, required = True,
                         help="Where to write the op list file")
    parser.add_argument( "--module_name", type = str, required = True,
                         help = "The name of the module to create, will create the file $module_name.v" )
    parser.add_argument( "--BW_in", type = int, required = True,
                         help = "The bitwidth of the inputs" )
    parser.add_argument( "--BW_out", type = int,
                         help = "The bitwidth of the outputs, defaults to BW_in if not given" )
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    matrix, no_in, no_out, initial_no_adds = twn.get_matrix( args.matrix_fname )
    matrix = twn.td_CSE( matrix )
    twn.write_output( args.cse_fname, matrix, initial_no_adds, no_in, no_out )
    twn.verify_tree( args.matrix_fname, args.cse_fname )
    if args.BW_out is None:
        BW_out = args.BW_in
    else:
        BW_out = args.BW_out
    f = open( args.module_name + ".v", "w" )
    f.write( twn.SMM_generate( args.cse_fname, args.module_name, args.BW_in, BW_out, twn.create_serial_add_op ) )
    f.close()
