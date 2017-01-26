'''
Change to Tensorflow Backend diemensions

Based on Residual block by Keunwoo Choi (keunwoo.choi@qmul.ac.uk)

It is based on "Deep Residual Learning for Image Recognition" (http://arxiv.org/abs/1512.03385)
and "Identity Mappings in Deep Residual Networks" (http://arxiv.org/abs/1603.05027).
'''
from keras.layers.core import Activation
from keras.layers.convolutional import Convolution2D
from keras.layers.normalization import BatchNormalization
from keras.layers import Input, merge
from keras.models import Model


def building_residual_block(input_shape, n_feature_maps, kernel_sizes=None, n_skip=2, is_subsample=False, subsample=None, dim='tf'):
    '''
    [1] Building block of layers for residual learning.
        Code based on https://github.com/ndronen/modeling/blob/master/modeling/residual.py
        , but modification of (perhaps) incorrect relu(f)+x thing and it's for conv layer

    [2] It can be used for both cases whether it subsamples or not.

    [3] In the short-cut connection, I used 1x1 convolution to increase #channel.
        It occurs when is_expand_channels == True

    input_shape = (None, num_channel, height, width) 'th'
    input_shape = (None, height, width, num_channel) 'tf'
    n_feature_maps: number of feature maps. In ResidualNet it increases whenever image is downsampled.
    kernel_sizes : list or tuple, (3,3) or [3,3] for example
    n_skip       : number of layers to skip
    is_subsample : If it is True, the layers subsamples by *subsample* to reduce the size.
    subsample    : tuple, (2,2) or (1,2) for example. Used only if is_subsample==True
    '''
    # ***** VERBOSE_PART *****
    print ('   - New residual block with')
    print ('      input shape:', input_shape)
    print ('      kernel size:', kernel_sizes)
    # is_expand_channels == True when num_channels increases.
    #    E.g. the very first residual block (e.g. 1->64, 3->128, 128->256, ...)
    if dim == 'tf':
        input_channel = input_shape[2]
    else:
        input_channel = input_shape[0]
    is_expand_channels = not (input_channel == n_feature_maps)
    if is_expand_channels:
        print ('      - Input channels: %d ---> num feature maps on out: %d' % (input_channel, n_feature_maps))
    if is_subsample:
        print ('      - with subsample:', subsample)
    kernel_row, kernel_col = kernel_sizes
    # set input
    x = Input(shape=(input_shape))
    # ***** SHORTCUT PATH *****
    if is_subsample:  # subsample (+ channel expansion if needed)
        shortcut_y = Convolution2D(n_feature_maps, kernel_row, kernel_col,
                                   subsample=subsample,
                                   border_mode='valid')(x)
    else:  # channel expansion only (e.g. the very first layer of the whole networks)
        if is_expand_channels:
            shortcut_y = Convolution2D(n_feature_maps, 1, 1, border_mode='same')(x)
        else:
            # if no subsample and no channel expension, there's nothing to add on the shortcut.
            shortcut_y = x
    # ***** CONVOLUTION_PATH *****
    conv_y = x
    for i in range(n_skip):
        conv_y = BatchNormalization(axis=1, mode=2)(conv_y)
        conv_y = Activation('relu')(conv_y)
        if i == 0 and is_subsample:  # [Subsample at layer 0 if needed]
            conv_y = Convolution2D(n_feature_maps, kernel_row, kernel_col,
                                   subsample=subsample,
                                   border_mode='valid')(conv_y)
        else:
            conv_y = Convolution2D(n_feature_maps, kernel_row, kernel_col, border_mode='same')(conv_y)
    # output
    y = merge([shortcut_y, conv_y], mode='sum')
    block = Model(input=x, output=y)
    print ('        -- model was built.')
    return block
