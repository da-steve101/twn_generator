Twn_Generator v0.1.2
====================

This package generates c or verilog code for convolutions in Ternary Neural Networks

Installation
------------
To install run

```
  pip3 install twn_generator
```

There are two example verilog use cases for computing the convolution

The first uses 16 bit adders to compute the convolution quickly.
The second computes the same result but computes the convolution using 4 bit serial adders.
This only has a quarter of the throughput but also a quarter of the area in adders.

To run the CSE and generate the adders, run:

```bash
   python3 run_cse_and_generate_example.py --matrix_fname data/conv1_weights.csv --cse_fname data/conv1_tern_op_list.csv --module_name lyr1 --BW_in 16
   python3 run_cse_and_generate_example.py --matrix_fname data/conv1_weights.csv --cse_fname data/conv1_tern_op_list.csv --module_name lyr1_serial --BW_in 4 --serial
```

This will generate 3 files:

 * lyr1.sv => the 16 bit adder version
 * lyr1_serial.sv => the 4 bit serial adder version
 * serial_adder.sv => a helper module implementing the serial adder

In the verilog/ directory the following can be used to verify the 16 bit adder example:

  * conv_windower.sv
  * windower_3x3_pad.sv
  * conv_windower_test.sv

For the 4 bit serial adder example:

  * conv_windower_serial.sv
  * from_serial.v
  * to_serial.v
  * windower_3x3_pad_serial_4.sv
  * conv_windower_serial_test.sv

The top level design modules are conv_windower.sv and conv_windower_serial.sv respectively.
The simulation test sources are conv_windower_test.sv and conv_windower_serial.sv

For more details on [CSE](docs/CSE.md)

For more details on [SMM](docs/SMM.md)
