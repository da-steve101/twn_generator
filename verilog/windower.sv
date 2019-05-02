`timescale 1ns / 1ps

/*
 This module computes the convolution using unrolled SMM
 To reduce fanout of the valid signals, it assumes that
 After the first valid signal, all following cycles in the image must
 have valid inputs for the rest of the image.
 This module assumes a 3x3 kernel with a stride of 1 and zero padding
*/

module windower
#(
  parameter IMG_SIZE = 32,
  parameter CH_IN = 3,
  parameter CH_OUT = 64,
  parameter BW = 16,
  parameter KERNEL_SIZE = 3,
  parameter ADDER_CYCLES = 1
)
(
input clock,
input reset,
input vld_in,
input [CH_IN-1:0][BW-1:0] in,
output vld_out,
output [KERNEL_SIZE*KERNEL_SIZE*CH_IN - 1:0][BW-1:0] window
);

reg [IMG_SIZE-1:0][CH_IN-1:0][BW-1:0] delay_1;
reg [IMG_SIZE-1:0][CH_IN-1:0][BW-1:0] delay_2;
reg [3*CH_IN - 1:0][BW-1:0] window_0;
reg [3*CH_IN - 1:0][BW-1:0] window_1;
reg [3*CH_IN - 1:0][BW-1:0] window_2;
reg [3*CH_IN - 1:0][BW-1:0] window_0_pad;
reg [3*CH_IN - 1:0][BW-1:0] window_1_pad;
reg [3*CH_IN - 1:0][BW-1:0] window_2_pad;
reg [IMG_SIZE+1:0] window_vld;
wire pad_top, pad_bot, pad_left, pad_right;
localparam LOG2_IMG_SIZE = $clog2( IMG_SIZE );
reg [LOG2_IMG_SIZE-1:0] row_cntr;
reg [LOG2_IMG_SIZE-1:0] col_cntr;
assign pad_top = ( row_cntr == 0 );
assign pad_bot = ( row_cntr == IMG_SIZE - 1 );
assign pad_left = ( col_cntr == 0 );
assign pad_right = ( col_cntr == IMG_SIZE - 1 );
reg img_vld;
assign vld_out = img_vld;
// need to swap conv order
assign window = { window_0_pad, window_1_pad, window_2_pad };   

always @( posedge clock ) begin
   if ( reset ) begin
      row_cntr <= 0;
      col_cntr <= 0;
      img_vld <= 0;
   end else begin
      if ( window_vld[IMG_SIZE+1] | row_cntr != 0 | col_cntr != 0 ) begin
	 col_cntr <= col_cntr + 1;
	 if ( col_cntr == IMG_SIZE - 1 ) begin
	    row_cntr <= row_cntr + 1;
	 end
      end
      img_vld <= window_vld[IMG_SIZE+1];
   end
   delay_1 <= { delay_1[IMG_SIZE-2:0], in };
   delay_2 <= { delay_2[IMG_SIZE-2:0], delay_1[IMG_SIZE-1] };
   window_0 <= { in, window_0[3*CH_IN - 1:CH_IN] };
   window_1 <= { delay_1[IMG_SIZE-1], window_1[3*CH_IN - 1:CH_IN]};
   window_2 <= { delay_2[IMG_SIZE-1], window_2[3*CH_IN - 1:CH_IN] };
   if ( pad_bot ) begin
      window_0_pad <= 0;
   end else begin
      window_0_pad[2*CH_IN - 1:CH_IN] <= window_0[2*CH_IN - 1:CH_IN];
      if ( pad_right ) begin
	 window_0_pad[3*CH_IN - 1:2*CH_IN] <= 0;
      end else begin
	 window_0_pad[3*CH_IN - 1:2*CH_IN] <= window_0[3*CH_IN - 1:2*CH_IN];
      end
      if ( pad_left ) begin
	 window_0_pad[CH_IN-1:0] <= 0;
      end else begin
	 window_0_pad[CH_IN-1:0] <= window_0[CH_IN-1:0];
      end
   end
   window_1_pad[2*CH_IN - 1:CH_IN] <= window_1[2*CH_IN - 1:CH_IN];
   if ( pad_right ) begin
      window_1_pad[3*CH_IN - 1:2*CH_IN] <= 0;
   end else begin
      window_1_pad[3*CH_IN - 1:2*CH_IN] <= window_1[3*CH_IN - 1:2*CH_IN];
   end
   if ( pad_left ) begin
      window_1_pad[CH_IN-1:0] <= 0;
   end else begin
      window_1_pad[CH_IN-1:0] <= window_1[CH_IN-1:0];
   end
   if ( pad_top ) begin
      window_2_pad <= 0;
   end else begin
      window_2_pad[2*CH_IN - 1:CH_IN] <= window_2[2*CH_IN - 1:CH_IN];
      if ( pad_right ) begin
	 window_2_pad[3*CH_IN - 1:2*CH_IN] <= 0;
      end else begin
	 window_2_pad[3*CH_IN - 1:2*CH_IN] <= window_2[3*CH_IN - 1:2*CH_IN];
      end
      if ( pad_left ) begin
	 window_2_pad[CH_IN-1:0] <= 0;
      end else begin
	 window_2_pad[CH_IN-1:0] <= window_2[CH_IN-1:0];
      end
   end
   window_vld <= { window_vld[IMG_SIZE+1:0], vld_in };
end

endmodule
