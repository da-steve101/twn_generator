Verilog Sparse Matrix Multiply generation
=========================================

This module generates verilog for a sparse matrix multiply module

Usage
-----

```python
   module_str = SMM_generate( fname_ops, module_name, BW_in, BW_out, create_op )
```

Where:

 * fname_ops => the file of ops generated from the CSE
 * module_name => the name of the generated module
 * BW_in => the bitwidth of the input
 * BW_out => the bitwidth of the output
 * create_op => a function that returns verilog for an adder

create_op has the following arguments:
```python
   create_op( names, op_code, shifts, BW_in, BW_out, module_name, reset_name, depth )
```

Where:

 * names => a list of length 4 with the names of [ output, input_a, input_b, input_c ]
 * op_code => a value between 0 and 7 meaning:
   * 0 -> output = - input_a - input_b - input_c
   * 1 -> output = - input_a - input_b + input_c
   * 2 -> output = - input_a + input_b - input_c
   * 3 -> output = - input_a + input_b + input_c
   * 4 -> output =   input_a - input_b - input_c
   * 5 -> output =   input_a - input_b + input_c
   * 6 -> output =   input_a + input_b - input_c
   * 7 -> output =   input_a + input_b + input_c
 * shifts => a list of 3 ints which is the amount of left shift ( can be negative )
 * BW_in => the BW of the inputs to the tree
 * BW_out => the BW of the outputs to the tree
 * module_name => the unique name to use for the op
 * reset_name => name of a reset to use
 * depth => the stage of the adder tree it is in, 0 for the first layer of adds

Some example create_op functions are provided:
 * create_serial_add_op
 * create_normal_add_op

Example code
------------

```python
  import twn_generator as twn
  input_fname = "conv4_tern_op_list.csv"
  module_name = "smm_conv4"
  BW_in = 4
  BW_out = 4
  twn.SMM_generate( input_fname, module_name, BW_in, BW_out, twn.create_serial_add_op )
  # need to include the serial_adder too for the create_serial_add_op
  twn.write_serial_adder_module( "serial_adder.v" )
  # if you want to generate smm_conv4.c and smm_conv4.h
  twn.write_tree_to_c( input_fname, module_name )
  # can also use twn.write_bn_relu_to_c( input_bn_f, r_shift, output_func )
  # input_bn_f => csv with 2 rows, a and b as integers
  # r_shift => right shift to do after the multiply
  # output_func => output func to write to, will write to output_func.c and output_func.h
```
