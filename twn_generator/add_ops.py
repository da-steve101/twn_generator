
def create_serial_add_op( names, op_code, shifts, BW_in, BW_out, module_name, reset_name, depth ):
    '''
    Creates an add or subtract operation ( input c is not allowed, no shifts allowed )
    names = [ out_name, a_name, b_name, c_name ]
    op_code = 0 -> - a - b - c ( not allowed in this implementation )
    op_code = 1 -> - a - b + c ( not allowed in this implementation )
    op_code = 2 -> - a + b - c
    op_code = 3 -> - a + b + c
    op_code = 4 ->   a - b - c
    op_code = 5 ->   a - b + c
    op_code = 6 ->   a + b - c
    op_code = 7 ->   a + b + c
    shifts = [ shift_a, shift_b, shift_c ] ( not allowed in this implementation )
    BW_in -> the bitwidth of the input
    BW_out -> the bitwidth of the output
    module_name -> the name to call the adder
    reset_name -> the reset to use, will assert the reset on the cycle before use
    depth -> how deep the op is down the tree, inputs have a depth of 0 ( not used in this op )
    '''
    assert names[3] == str(BW_out) + "'h0", "Three inputs not implemented in this adder"
    assert shifts[0] == 0 and shifts[1] == 0, "Shift registers not implemented in this adder"
    # deal with neg regs
    op_code = op_code >> 1
    if names[2] == str(BW_out) + "'h0" and op_code == 0:
        op_code = 1;
    assert op_code != 0, "Cannot be both negative inputs for serial adder for module " + module_name
    neg_b = ( op_code != 3 )*1
    # swap the order so input a is positive
    if op_code == 1:
        names[1], names[2] = ( names[2], names[1] )
    ser_add_module = '''wire [''' + str( BW_in - 1 ) + ":0] " + names[0] + ''';
serial_adder #(
  .neg_b(''' + str(neg_b) + '''),
  .BW(''' + str(BW_in) + ''')
) ''' + module_name + ''' (
 .clk(clock),
 .reset(''' + reset_name + '''),
 .a(''' + names[1] + '''),
 .b(''' + names[2] + '''),
 .c(''' + names[0] + ''')
);
'''
    return ser_add_module, BW_in

def write_serial_adder_module( fname ):
    f = open( fname, "w" )
    f.write( """
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
""" )
    f.close()

def create_normal_add_op( names, op_code, shifts, BW_in, BW_out, module_name, reset_name, depth ):
    '''
    Creates an add or subtract operation
    names = [ out_name, a_name, b_name, c_name ]
    op_code = 0 -> - a - b - c
    op_code = 1 -> - a - b + c
    op_code = 2 -> - a + b - c
    op_code = 3 -> - a + b + c
    op_code = 4 ->   a - b - c
    op_code = 5 ->   a - b + c
    op_code = 6 ->   a + b - c
    op_code = 7 ->   a + b + c
    shifts = [ shift_a, shift_b, shift_c ]
    BW_in -> the bitwidth of the input
    BW_out -> the bitwidth of the output
    module_name -> the name to call the adder
    reset_name -> the reset to use, will assert the reset on the cycle before use ( not used in this op )
    depth -> how deep the op is down the tree, inputs have a depth of 0 ( not used in this op )
    '''
    op_str = ""
    op_mod = 4
    for n, s in zip( names[1:], shifts ):
        if op_code < op_mod:
            op_str += " - "
        elif op_mod != 4:
            op_str += " + "
        op_code = op_code % op_mod
        op_mod = op_mod >> 1
        op_str += "( $signed( " + n + " ) "
        if s < 0:
            op_str += " >> " + str( - s ) + " )"
        elif s > 0:
            op_str += " << " + str( s ) + " )"
        else:
            op_str += ")"
    add_op = '''reg [''' + str( BW_in - 1 ) + ":0] " + names[0] + ''';
always @( posedge clock ) begin
''' + names[0] + " <= " + op_str + ''';
end
'''
    return add_op, BW_in
