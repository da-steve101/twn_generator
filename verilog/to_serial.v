
module to_serial
#(
  parameter BW = 16,
  parameter CYCS = 4,
  parameter VEC_LEN = 27
)
(
 input clock,
 input vld_in,
 input [VEC_LEN-1:0][BW-1:0] in,
 output vld_out,
 output [VEC_LEN-1:0][(BW/CYCS)-1:0] out
);

reg [CYCS-1:0] vlds = 0;
reg [VEC_LEN-1:0][BW-1:0] data_reg;

assign vld_out = vlds[CYCS-1];
   
always @( posedge clock )
  begin
     if ( vld_in ) begin
	vlds <= ( 1 << CYCS ) - 1;
     end else begin
	vlds <= { vlds[CYCS-2:0], 1'b0 };
     end
  end

genvar i;
generate
   for ( i = 0; i < VEC_LEN; i++ ) begin
      assign out[i] = data_reg[i][(BW/CYCS)-1:0];
      always @( posedge clock ) begin
	 if ( vld_in ) begin
	    data_reg[i] <= in[i];
	 end else begin
	    data_reg[i][BW-(BW/CYCS)-1:0] <= data_reg[i][BW-1:(BW/CYCS)];
	 end
      end
   end
endgenerate
endmodule
