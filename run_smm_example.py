#! /usr/bin/python3

import argparse
import SMM

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--input_op_list", type = str, required = True,
                         help="The op list file to generate from, probably output from CSE")
    parser.add_argument( "--module_name", type = str, required = True,
                         help = "The name of the module to create, will create the file $module_name.v" )
    parser.add_argument( "--BW_in", type = int, required = True,
                         help = "The bitwidth of the inputs" )
    parser.add_argument( "--BW_out", type = int,
                         help = "The bitwidth of the outputs, defaults to BW_in if not given" )
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    if args.BW_out is None:
        BW_out = args.BW_in
    else:
        BW_out = args.BW_out
    f = open( args.module_name + ".v", "w" )
    f.write( SMM.SMM_generate( args.input_op_list, args.module_name, args.BW_in, BW_out, SMM.create_serial_add_op ) )
    f.close()
