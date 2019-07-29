#! /usr/bin/python3

import numpy as np
from scipy import signal
from skimage.measure import block_reduce

def round_to( x, bits_prec ):
    factor = 1 << bits_prec
    return np.round( x * factor )/factor

def floor_to( x, bits_prec ):
    factor = 1 << bits_prec
    return np.floor( x * factor )/factor

def get_ternary( x ):
    '''
    Useful for networks such as ternary weight networks where
    the values of the network is -a,0,a
    This function returns the ( ( weights as -1,0,1 ), a )
    '''
    x_flat = x.flatten()
    scaling_factor = np.mean(abs(x_flat[abs(x_flat) > 0]))
    tri_weights = np.round(x/scaling_factor).astype( int )
    return tri_weights, scaling_factor

def conv2d( img, conv_weights, padding = 'same' ):
    '''
    img => img to convolve
    conv_weights => the weights for the convolution
    padding => "same" or "valid"
    '''
    filter_out = []
    for fno in range( conv_weights.shape[-1] ):
        ch_sum = 0
        for chno in range( conv_weights.shape[-2] ):
            conv_window = np.flip( np.flip( conv_weights[:,:,chno,fno], 0 ), 1 )
            ch_sum += signal.convolve2d( img[:,:,chno], conv_window, mode = padding )
        filter_out += [ ch_sum ]
    filter_out = np.array( filter_out )
    return np.transpose( filter_out, [ 1, 2, 0 ] )

def conv1d( img, conv_weights, padding = "same" ):
    '''
    img => img to convolve
    conv_weights => the weights for the convolution
    padding => "same" or "valid"
    '''
    filter_out = []
    for fno in range( conv_weights.shape[-1] ):
        ch_sum = 0
        for chno in range( conv_weights.shape[-2] ):
            conv_window = np.flip( conv_weights[:,chno,fno], 0 )
            ch_sum += signal.convolve( img[:,chno], conv_window, mode = padding )
        filter_out += [ ch_sum ]
    filter_out = np.array( filter_out )
    return np.transpose( filter_out, [ 1, 0 ] )

def get_AB( mean, var, gamma, beta, scaling_factor, bias = 0, thres = 10**15 ):
    '''
    Merge BN and TWN variables into a transform: ax + b
    returns ( a, b )
    '''
    mean = mean - bias
    stddev = np.sqrt( var )
    a = gamma / stddev
    a = a * ( a < thres ) # if very big then prob is ignored anyway: ie) stddev = 0
    b = beta - a * mean
    a = a * scaling_factor
    return ( a, b )

def get_AB_quantized( mean, var, gamma, beta, eta_r, is_round = True ):
    '''
    Get variables to perform batch norm with a limited number of bits in and out
    mean, var, gamma, beta => floating point variables from batch norm
    eta_r => the amount to input is scaled by
    is_round => if a rounding function was used to quantize or if False, assumes ceil function
    returns ( a, b, x_min, x_max )
    '''
    a = gamma / np.sqrt( var )
    b = beta - a * mean
    a *= eta_r
    if is_round:
        b += 0.4999999
        x_min = ( 1/2 - b )/a
        x_max = (1 - 1/2 - b )/a
    else:
        b += 0.999999
        x_min = -b/a
        x_max = ( 1 - b )/a
    return a, b, x_min, x_max

def maxpool2d( img, kern_and_stride = 2 ):
    return block_reduce( img, (kern_and_stride, kern_and_stride, 1), np.max )

def maxpool1d( img, kern_and_stride = 2 ):
    return block_reduce( img, (kern_and_stride, 1), np.max )

def relu( img ):
    return img * ( img > 0 )
