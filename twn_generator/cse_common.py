
import numpy as np
import csv
import math

def size_of_tree( matrix ):
    return np.sum( np.absolute( matrix ) ) - matrix.shape[1]

def create_stage( curr_idx, idxs ):
    # group by 2 and create ops
    op_list = []
    for i in range( int( math.ceil( len(idxs) / 2 ) ) ):
        a = idxs[2*i]
        if len(idxs) < 2*i+2:
            b = [ -1, 0, False ]
        else:
            b = idxs[2*i + 1]
        add_op = 4*a[2] + 2*b[2]
        op_new = [ curr_idx, a[0], b[0], -1, add_op, 0, 0, 0 ]
        curr_idx += 1
        op_list += [ op_new ]
    return op_list, curr_idx

def create_stage_ternary( curr_idx, idxs ):
    # group by 3 and create ops
    op_list = []
    for i in range( int( math.ceil( len(idxs) / 3 ) ) ):
        a = idxs[3*i]
        if len(idxs) < 3*i+2:
            b = [ -1, 0, False ]
        else:
            b = idxs[3*i + 1]
        if len(idxs) < 3*i+3:
            c = [ -1, 0, False ]
        else:
            c = idxs[3*i + 2]
        add_op = 4*a[2] + 2*b[2] + 1*c[2]
        op_new = [ curr_idx, a[0], b[0], c[0], add_op, 0, 0, 0 ]
        curr_idx += 1
        op_list += [ op_new ]
    return op_list, curr_idx

def create_ops_for_tree( curr_idx, curr_idxs, use_tern = False ):
    # curr_idxs = [ ( idx, depth_avail, is_pos ) ]
    if len(curr_idxs) == 0:
        return ( [], curr_idx, -1, 0 )
    curr_d = 0
    op_list = []
    reserves = []
    while len(reserves) > 0 or len(curr_idxs) > 1 or len(op_list) < 1:
        reserves = [ x for x in curr_idxs if x[1] > curr_d ]
        to_reduce = [ x for x in curr_idxs if x[1] <= curr_d ]
        if use_tern:
            reduced_ops, curr_idx = create_stage_ternary( curr_idx, to_reduce )
        else:
            reduced_ops, curr_idx = create_stage( curr_idx, to_reduce )
        curr_idxs = [ ( x[0], curr_d + 1, True )  for x in reduced_ops ] + reserves
        op_list += reduced_ops
        curr_d += 1
    output_idx = op_list[-1][0]
    return op_list, curr_idx, output_idx, curr_d

def combine_dep( dep_a, dep_b ):
    # merge two rows back together
    for x in dep_b:
        dep_a[x] = dep_b[x]
    return dep_a

def get_dependancies( idxs, matrix, no_in, no_out ):
    # merge certain indexes back together
    dependancies = {}
    for i in idxs:
        dependancies[ i ] = list( np.nonzero( matrix[no_in:,i] )[0] + no_out )
        dependancies = combine_dep( dependancies,
                                    get_dependancies( dependancies[ i ], matrix, no_in, no_out )
        )
    return dependancies

def make_tree( matrix, no_in, no_out ):
    '''
    Convert the matrix to the op list
    '''
    dependancies = {}
    output_depths = {}
    for j in range( no_out ):
        idxs = list( np.nonzero( matrix[no_in:,j] )[0] + no_out )
        dependancies[j] = idxs
        dependancies = combine_dep( dependancies,
                                    get_dependancies( idxs, matrix, no_in, no_out ) )
    outputs = {}
    op_list = []
    op_idx = no_in
    max_depth = 0
    while len( outputs ) < len(dependancies):
        for x in dependancies:
            if x not in outputs: # haven't already done
                # check all dependancies are resolved otherwise skip for now
                dep_depths = [ output_depths[ y ] for y in dependancies[x] if y in output_depths ]
                if len( dep_depths ) == len(dependancies[x]):
                    idxs = np.nonzero( matrix[:,x] )[0]
                    idxs_in = []
                    for i in idxs:
                        j = i
                        d = 0
                        if i >= no_in:
                            j = outputs[ i + no_out - no_in ]
                            d = output_depths[ i + no_out - no_in ]
                        assert matrix[i,x] != 0, "has dependancy with zero? - invalid matrix"
                        idxs_in += [ (j, d, matrix[i,x] > 0) ]
                    new_ops, op_idx, output_idx, curr_d = create_ops_for_tree( op_idx, idxs_in )
                    outputs[ x ] = output_idx
                    output_depths[ x ] = curr_d
                    if curr_d > max_depth:
                        max_depth = curr_d
                    op_list += new_ops
    return op_list, [ outputs[i] for i in range( no_out ) ], max_depth

def reverse_check_result( orig_mat, new_mat ):
    '''
    A verification step that the tree is valid
    '''
    no_in = orig_mat.shape[1]
    no_out = orig_mat.shape[0]
    # replace elim outputs with full expression
    for i in range( new_mat.shape[0] - no_out ):
        vec_idx_orig = np.nonzero( new_mat[no_out+i,:] )[0]
        update_idx = np.nonzero( new_mat[:,no_in+i] )[0]
        vec_idx = np.tile( vec_idx_orig, len(update_idx) )
        update_idx = np.repeat( update_idx, len(vec_idx_orig) )
        vec = new_mat[no_out+i,vec_idx]
        new_mat[update_idx,vec_idx] += vec*new_mat[update_idx,no_in+i]
        new_mat[no_out+i,vec_idx_orig] -= new_mat[no_out+i,vec_idx_orig]
    return np.sum( new_mat[:no_out,:no_in] == orig_mat ) == no_in*no_out

def get_matrix( fname ):
    '''
    Load the matrix
    '''
    f = open( fname )
    rdr = csv.reader( f )
    data = [ [ int(y) for y in x ] for x in rdr ]
    matrix = np.transpose( np.array( data, dtype = np.int16 ) )
    no_in = matrix.shape[1]
    no_out = matrix.shape[0]
    print( "no_in = " + str(no_in) + ", no_out = " + str(no_out) )
    initial_no_adds = size_of_tree( matrix )
    print( "initial matrix is " + str( initial_no_adds  ) )
    return matrix, no_in, no_out, initial_no_adds

def write_output( fname, matrix, initial_no_adds, no_in, no_out, remove_neg_ops = True ):
    '''
    Write the CSE result to a file
    '''
    final_no_adds = size_of_tree( matrix )
    print( "improvement is from " + str( initial_no_adds ) + " to " +
           str( final_no_adds ) + " or " + str( final_no_adds*100/initial_no_adds ) + "%" )
    f_out = open( fname, "w" )
    wrt = csv.writer( f_out )
    tree_ops, outputs, max_depth = make_tree( np.transpose( matrix ), no_in, no_out )
    tmp = wrt.writerow( outputs )
    for x in tree_ops:
        tmp = wrt.writerow( x )
    f_out.close()
    if remove_neg_ops:
        remove_negate_ops( fname )
    return max_depth

def compute_op( a, b, c, op_code ):
    if op_code == 0:
      return - a - b - c
    if op_code == 1:
      return - a - b + c
    if op_code == 2:
      return - a + b - c
    if op_code == 3:
      return - a + b + c
    if op_code == 4:
      return a - b - c
    if op_code == 5:
      return a - b + c
    if op_code == 6:
      return a + b - c
    return a + b + c

def remove_negate_ops( fname ):
    '''
    Move any ops that have double negate
    This is necessary for serial adders as it isn't hardware friendy to implement
    '''
    f = open( fname )
    rdr = csv.reader( f )
    data = [ x for x in rdr ]
    f.close()
    f_out = open( fname, "w" )
    wrt = csv.writer( f_out )
    negate_ops = set([])
    output_idxs = data[0]
    output_idxs_set = set( [ int(x) for x in output_idxs ] )
    negate_outputs = []
    new_rows = []
    last_op = -1
    for x in data[1:]:
        new_row = x
        op_code = int( x[4] )
        if int( x[1] ) in negate_ops:
            op_code = ( op_code + 4 ) % 8
        if int( x[2] ) in negate_ops:
            op_code = ( ( op_code + 2 ) % 4 ) + 4*( op_code >> 2 )
        if int( x[3] ) in negate_ops:
            op_code = ( ( op_code + 1 ) % 2 ) + 2*( op_code >> 1 )
        new_row[4] = str( op_code )
        is_neg = op_code == 0 or ( int(x[3]) < 0 and op_code < 2 )
        if is_neg:
            negate_ops.add( int(x[0]) )
            new_row[4] = str( 7 - op_code )
            if int( x[0] ) in output_idxs_set:
                negate_outputs += [ int(x[0]) ]
        new_rows += [ new_row ]
        last_op = int(new_row[0])
    # add more regs that fix negated outputs
    for i in negate_outputs:
        last_op += 1
        new_row = [ last_op, i, -1, -1, 0, 0, 0, 0 ]
        for j, oi in enumerate( output_idxs ):
            if oi == str(i):
                output_idxs[j] = str(last_op)
                break
        new_rows += [ new_row ]
    wrt.writerow( output_idxs )
    for new_row in new_rows:
        wrt.writerow( new_row )
    f_out.close()

def verify_tree( fname, fname_out ):
    '''
    Verify that the op list generated matches the matrix input
    '''
    matrix, no_in, no_out, initial_no_adds = get_matrix( fname )
    f_t = open( fname_out )
    rdr = csv.reader( f_t )
    ops = [ [ int(y) for y in x ] for x in rdr ]
    outputs = ops[0]
    tmp_inputs = np.random.randint( -(1<<12), 1 << 12, no_in )
    expected_out = np.matmul( matrix, tmp_inputs )
    tmp_vals = {}
    for op in ops[1:]:
        a = tmp_inputs[op[1]] if op[1] not in tmp_vals else tmp_vals[op[1]]
        if op[2] >= 0:
            b = tmp_inputs[op[2]] if op[2] not in tmp_vals else tmp_vals[op[2]]
        else:
            b = 0
        if op[3] >= 0:
            c = tmp_inputs[op[3]] if op[3] not in tmp_vals else tmp_vals[op[3]]
        else:
            c = 0
        tmp_vals[op[0]] = compute_op( a, b, c, op[4] )
    for i, o in enumerate( outputs ):
        if o < 0:
            continue
        assert expected_out[i] == tmp_vals[o], "must match expected output from tree for output " + str(o)
    return True
