`timescale 1ns / 1ps

/*
 This module computes the convolution using unrolled SMM
 To reduce fanout of the valid signals, it assumes that
 After the first valid signal, all following cycles in the image must
 have valid inputs for the rest of the image.
 This module assumes a 3x3 kernel with a stride of 1 and zero padding
*/

module conv_windower
#(
  parameter IMG_SIZE = 32,
  parameter CH_IN = 3,
  parameter CH_OUT = 64
)
(
input clock,
input reset,
input vld_in,
input [CH_IN-1:0][15:0] in,
output vld_out,
output [CH_OUT-1:0][15:0] out
);

wire img_vld;
wire [9*CH_IN - 1:0][15:0] window;   

windower
#(
  .IMG_SIZE(IMG_SIZE),
  .CH_IN(3),
  .CH_OUT(CH_OUT),
  .BW(16)
) lyr1_windower
(
.clock(clock),
.reset(reset),
.vld_in(vld_in),
.in(in),
.vld_out( img_vld ),
.window( window )
);

lyr1 lyr1_inst (
.clock(clock),
.reset(1),
.vld_in(img_vld),
.in( window ),
.vld_out( vld_out ),
.out( out )
);

endmodule
