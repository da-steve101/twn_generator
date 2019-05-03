`timescale 1ns / 1ps

/*
 This module computes the convolution using unrolled SMM
 To reduce fanout of the valid signals, it assumes that
 After the first valid signal, all following cycles in the image must
 have valid inputs for the rest of the image.
 As this example is using 4 bit adders, this means 1 input every 4 cycles
 This module assumes a 3x3 kernel with a stride of 1 and zero padding
*/

module conv_windower_serial
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

wire ser_vld;
wire [CH_IN - 1:0][3:0] ser_data;

to_serial
#(
  .BW(16),
  .CYCS(4),
  .VEC_LEN(CH_IN)
) to_serial_inst
(
 .clock(clock),
 .vld_in(vld_in),
 .in(in),
 .vld_out(ser_vld),
 .out( ser_data )
);

wire img_vld;
wire [9*CH_IN - 1:0][3:0] window;

windower_3x3_pad_serial_4
#(
  .IMG_SIZE(IMG_SIZE),
  .CH_IN(3),
  .CH_OUT(CH_OUT),
  .BW(4)
) lyr1_windower
(
.clock(clock),
.reset(reset),
.vld_in(ser_vld),
.in(ser_data),
.vld_out( img_vld ),
.window( window )
);
   
wire pred_vld;
wire [CH_OUT - 1:0][3:0] pred_data;
reg [1:0] rst_cntr;
always @( posedge clock )
  begin
     if ( reset ) begin
	rst_cntr <= 0;
     end else begin
	if ( img_vld ) begin
	   rst_cntr <= rst_cntr + 1;
	end
     end
  end
lyr1_serial lyr1_inst (
.clock(clock),
.reset( ( rst_cntr == 3 ) | !img_vld ),
.vld_in(img_vld),
.in( window ),
.vld_out( pred_vld ),
.out( pred_data )
);
   
from_serial
#(
  .BW(16),
  .CYCS(4),
  .VEC_LEN(CH_OUT)
) from_serial_inst
(
 .clock(clock),
 .vld_in(pred_vld),
 .in(pred_data),
 .vld_out(vld_out),
 .out( out )
);

endmodule
