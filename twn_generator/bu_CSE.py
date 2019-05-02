#! /usr/bin/python3

import csv
import numpy as np
import sys
import math

def get_pattern_mat( matrix, pattern_matrix, update_idxs, rm_idxs ):
    '''
    create a cache of all common subexpressions that can be removed
    '''
    rm_idxs = [ x for x in rm_idxs ]
    rm_idxs = sorted( rm_idxs, reverse=True )
    for idx in rm_idxs:
        del pattern_matrix[idx]
        for i in range( 0, idx ):
            del pattern_matrix[i][0][idx - i - 1]
            del pattern_matrix[i][1][idx - i - 1]
    # change update_idxs now those idxs have been removed
    for idx in rm_idxs:
        update_idxs = [ x if x < idx else x - 1 for x in update_idxs ]
    # recalculate the indexs that have changed
    for idx in update_idxs:
        if len(pattern_matrix) <= idx:
            pattern_matrix += [[[-1],[-1],-1]] # just filler
        res_mat_pos = np.absolute( matrix + np.tile( matrix[idx,:], [ matrix.shape[0], 1 ] ) ) > 1
        res_mat_pos_sum = np.sum( res_mat_pos, 1 )
        res_mat_neg = np.absolute( matrix - np.tile( matrix[idx,:], [ matrix.shape[0], 1 ] ) ) > 1
        res_mat_neg_sum = np.sum( res_mat_neg, 1 )
        for i in range( idx ):
            if len( pattern_matrix[i][0] ) == idx - i - 1:
                pattern_matrix[i][0] += [ res_mat_pos_sum[i] ]
                pattern_matrix[i][1] += [ res_mat_neg_sum[i] ]
            else:
                pattern_matrix[i][0][idx - i - 1] = res_mat_pos_sum[i]
                pattern_matrix[i][1][idx - i - 1] = res_mat_neg_sum[i]
        for i in range( idx ):
            pattern_matrix[i][2] = max( pattern_matrix[i][0] + pattern_matrix[i][1] )
        if matrix.shape[0] > idx + 1:
            pattern_matrix[idx] = [ res_mat_pos_sum.tolist()[idx+1:],
                                    res_mat_neg_sum.tolist()[idx+1:],
                                    np.max( res_mat_pos_sum.tolist()[idx+1:] + res_mat_neg_sum.tolist()[idx+1:] ) ]
    return pattern_matrix

def get_common_idx( pattern_matrix ):
    # how many terms does the largest common expression have
    max_common = np.max( [ x[2] for x in pattern_matrix ] )
    common_idxs = []
    # where does the largest expression size occur
    for idx, x in enumerate( pattern_matrix ):
        if x[2] >= max_common:
            for j, x in enumerate( pattern_matrix[idx][0] ):
                if x >= max_common:
                    common_idxs += [ (idx, j + idx + 1, True) ]
            for j, x in enumerate( pattern_matrix[idx][1] ):
                if x >= max_common:
                    common_idxs += [ (idx, j + idx + 1, False) ]
    return max_common, common_idxs

def find_finished_idxs( pattern_matrix ):
    '''
    Find indexs that cannot be eliminated further
    '''
    rm_idxs = set( range( len( pattern_matrix ) ) )
    for i, row in enumerate( pattern_matrix ):
        # not the last row ...
        if ( row[2] < 0 or row[2] > 1 ) and i in rm_idxs:
            rm_idxs.remove(i)
    for i, row in enumerate( pattern_matrix ):
        for rowidx in [0,1]:
            for j in [ j for j in rm_idxs if i < j ]:
                x = row[rowidx][j-i-1]
                if x > 1:
                    rm_idxs.remove(j)
    return rm_idxs

def reorder_pattern( pattern ):
    # flip so the first number is positive
    for x in pattern:
        if x > 0:
            return ( pattern, False )
        if x < 0:
            return ( -pattern, True )
    return ( pattern, False )

def get_patterns_and_negations( matrix, common_idxs ):
    '''
    Check all the largest subexpressions to find the most common one
    '''
    patterns = []
    negations = []
    for idx_a, idx_b, is_pos in common_idxs:
        sign = -1
        if is_pos:
            sign = 1
        pattern = (np.absolute( matrix[idx_a] + sign*matrix[idx_b] ) > 1)*matrix[idx_a]
        pattern, neg = reorder_pattern( pattern )
        negations += [ neg ]
        patterns += [ pattern ]
    # find most common
    patterns = [ list(x) for x in patterns ]
    patterns = sorted( enumerate( patterns ), key=lambda x:x[1] )
    return patterns, negations

def get_pos_neg( common_idx, negation ):
    res_pos = []
    res_neg = []
    if common_idx[2]:
        if negation:
            res_neg = common_idx[:2]
        else:
            res_pos = common_idx[:2]
    else:
        if negation:
            res_pos = [ common_idx[1] ]
            res_neg = [ common_idx[0] ]
        else:
            res_pos = [ common_idx[0] ]
            res_neg = [ common_idx[1] ]
    return list(set(res_pos)), list(set(res_neg))

def find_most_common( matrix, common_idxs ):
    '''
    Look at all subexpressions, then choose the largest. If there is a tie choose the most common
    '''
    patterns, negations = get_patterns_and_negations( matrix, common_idxs )

    # group and find largest group ...
    best_idx = 0
    best_size = 0
    curr_start = 0
    curr_size = 0
    for idx, pattern in enumerate( [ x[1] for x in patterns ] ):
        if patterns[curr_start][1] == pattern:
            curr_size += 1
        else:
            curr_size = 1
            curr_start = idx
        if curr_size > best_size:
            best_idx = curr_start
            best_size = curr_size
    pattern = patterns[best_idx][1]
    idxs = [ x for x in [ patterns[i][0] for i in range( best_idx, best_idx + best_size ) ] ]

    res_pos = []
    res_neg = []
    for i in idxs:
        tmp_pos, tmp_neg = get_pos_neg( common_idxs[i], negations[i] )
        res_pos += tmp_pos
        res_neg += tmp_neg
    return pattern, list(set(res_pos)), list(set(res_neg))

def update_matrix( matrix, idxs_pos, idxs_neg, pattern, rm_idxs ):
    '''
    Apply the changes needed
    '''
    # first eliminate common expr
    for i in idxs_pos:
        matrix[i,:] = matrix[i,:] - pattern
    for i in idxs_neg:
        matrix[i,:] = matrix[i,:] + pattern
    # add new row to matrix
    matrix = np.vstack( [ matrix, pattern ] )
    # add new col to matrix
    matrix = np.hstack( [ matrix, np.zeros( ( matrix.shape[0], 1 ), dtype = np.int16 ) ] )
    for i in idxs_pos:
        matrix[i,-1] = 1
    for i in idxs_neg:
        matrix[i,-1] = -1
    return_mat = [ ( matrix[i,:], i ) for i in rm_idxs ]
    matrix = matrix[np.array( [ i for i in range( matrix.shape[0] ) if i not in set(rm_idxs) ] ),:]
    return matrix, return_mat

def is_intersection( existing_patterns, new_pattern ):
    '''
    Check if a row matches a pattern
    '''
    p = np.absolute( np.array( new_pattern ) )
    for ep in existing_patterns:
        res = p.dot( np.absolute( np.array(ep) ) )
        if res > 0:
            return True
    return False

def fast_update_pat_2_join( matrix, pattern_matrix ):
    '''
    When subexpressions of size 2 left, the original approach starts to get very slow and use a lot of memory.
    Compute all subexpression eliminations remaining at once instead
    '''
    print( "Only subexpressions of size 2 left ..." )
    max_common, common_idxs = get_common_idx( pattern_matrix )
    if max_common < 2:
        return max_common, matrix, []
    patterns, negations = get_patterns_and_negations( matrix, common_idxs )
    # determine non-intersecting patterns
    idx_to_pattern = {}
    chosen_idxs = []
    for p in patterns:
        idx_a, idx_b, neg = common_idxs[p[0]]
        if idx_a not in idx_to_pattern:
            idx_to_pattern[idx_a] = []
        if idx_b not in idx_to_pattern:
            idx_to_pattern[idx_b] = []
        if not is_intersection( idx_to_pattern[idx_a], p[1] ) and not is_intersection( idx_to_pattern[ idx_b ], p[1] ):
            idx_to_pattern[ idx_a ] += [ p[1] ]
            idx_to_pattern[ idx_b ] += [ p[1] ]
            chosen_idxs += [ p ]
    print( "There are " + str(len(chosen_idxs)) + " non intersecting patterns of size 2 that can be removed" )
    no_pad = 0
    update_idxs = []
    for i, p in chosen_idxs:
        res_pos, res_neg = get_pos_neg( common_idxs[i], negations[i] )
        pattern = np.concatenate( ( np.array( p, dtype = np.int16 ), np.array( [0]*no_pad, dtype = np.int16 ) ) )
        no_pad += 1
        matrix, return_mat = update_matrix( matrix, res_pos, res_neg, pattern, [] )
        update_idxs += res_pos + res_neg
    update_idxs = list(set(update_idxs)) + list(range( matrix.shape[0] - no_pad, matrix.shape[0] ))
    update_idxs.sort()
    return max_common, matrix, update_idxs

def bu_CSE( matrix ):
    pattern_matrix = []
    finished_rows = []
    update_idxs = list( range( matrix.shape[0] ) )
    rm_idxs = []
    most_common_count = 3
    pattern_pos = []
    pattern_neg = []
    # orig_mat = matrix.copy()
    while most_common_count > 1:
        # get the new set of subexpressions
        pattern_matrix = get_pattern_mat( matrix, pattern_matrix, update_idxs, rm_idxs )
        if most_common_count > 2 or len(pattern_pos) + len(pattern_neg) > 2:
            # get the largest most common subexpression
            most_common_count, common_idxs = get_common_idx( pattern_matrix )
            pattern, pattern_pos, pattern_neg = find_most_common( matrix, common_idxs )
            rm_idxs = find_finished_idxs( pattern_matrix )
            # apply changes
            matrix, return_mat = update_matrix( matrix, pattern_pos, pattern_neg, pattern, rm_idxs )
            finished_rows = return_mat + finished_rows
            ''' verify result => makes it run very slow
            new_mat = matrix.copy()
            for x, i in finished_rows:
                tmp = np.concatenate( ( np.array( x, dtype=np.int16 ),  np.zeros( ( new_mat.shape[1] - len(x) ), dtype = np.int16 ) ) )
                new_mat = np.vstack( [ new_mat[:i,:], tmp, new_mat[i:,:] ] )
            assert reverse_check_result( orig_mat, new_mat ), "must have same matrix originally"
            '''
            # indexs that need to be updated in the pattern matrix
            update_idxs = pattern_pos + pattern_neg + [matrix.shape[0] + len(return_mat) - 1]
            print( str(len(pattern_pos) + len(pattern_neg)) +
                   " expressions have a common subexpression of size "
                   + str(most_common_count) + " to be eliminated"  )
        else:
            rm_idxs = []
            most_common_count, matrix, update_idxs = fast_update_pat_2_join( matrix, pattern_matrix )
    for x, i in finished_rows:
        tmp = np.concatenate( ( np.array( x, dtype=np.int16 ),  np.zeros( ( matrix.shape[1] - len(x) ), dtype = np.int16 ) ) )
        matrix = np.vstack( [ matrix[:i,:], tmp, matrix[i:,:] ] )
    return matrix
