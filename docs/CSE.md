Common Subexpression Elimination
================================

These files perform greedy subexpression elimination searches.
There are two approaches:

 * Top Down CSE
 * Bottom Up CSE

Usage
-----

The CSE expects file containing a matrix of values containing 1,0 or -1 only.
The matrix having x rows in the file and y columns means there are x inputs and y outputs.
For the following example:

 * fname = the input file
 * fname_out = the output op list

~~~
    import twn_generator as twn
    matrix, no_in, no_out, initial_no_adds = twn.get_matrix( fname )
    matrix = twn.bu_CSE( matrix ) # perform bottom up subepression elimination
    # or matrix = twn.td_CSE( matrix ) to perform top down
    # turn the matrix into an ops list to $fname_out
    twn.write_output( fname_out, matrix, initial_no_adds, no_in, no_out )
    # verify that the tree generated computes the same result as the matrix
    twn.verify_tree( fname, fname_out )
~~~

Top Down CSE
------------

Builds the tree from the top at the inputs to the outputs.
This is typically better if the number of inputs is smaller than the number of outputs.

Bottom Up CSE
-------------

Builds the tree from the bottom of the tree to the top.
This tends to find better solutions than top down CSE if there are more inputs than outputs.
It is more computationally intensive and requires more memory

