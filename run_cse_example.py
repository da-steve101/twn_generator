#! /usr/bin/python3

import CSE
import sys

if __name__ == "__main__":
    fname = sys.argv[1]
    fname_out = sys.argv[2]
    matrix, no_in, no_out, initial_no_adds = CSE.get_matrix( fname )
    matrix = CSE.td_CSE( matrix )
    CSE.write_output( fname_out, matrix, initial_no_adds, no_in, no_out )
    CSE.verify_tree( fname, fname_out )
