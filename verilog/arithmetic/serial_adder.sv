`timescale 1ns / 1ps

module serial_adder
#(
 parameter neg_b = 0,
 parameter BW = 16
)
(
 input 		 clk,
 input 		 reset,
 input [BW-1:0]  a,
 input [BW-1:0]  b,
 output [BW-1:0] c
 );
   reg carry_reg;
   reg [BW-1:0] data_out_reg;
   wire [BW-1:0] b_neg;
   wire [BW:0] 	 result;
   assign b_neg = neg_b ? ~b : b;
   assign result = a + b_neg + carry_reg;
   assign c = data_out_reg;
always @( posedge clk ) begin
   if ( reset ) begin
      carry_reg <= neg_b;
   end else begin
      carry_reg <= result[BW];
   end
   data_out_reg <= result[BW-1:0];
end
endmodule
