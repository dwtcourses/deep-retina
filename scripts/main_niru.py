"""
Main script for training deep retinal models

"""

from __future__ import absolute_import
from deepretina.models import sequential, convnet, train
from deepretina.experiments import Experiment
from deepretina.io import Monitor, main_wrapper


@main_wrapper
def fit_convnet(cells, train_stimuli, exptdate, readme=None):
    """Main script for fitting a convnet
    
    author: Niru Maheswaranathan
    """

    stim_shape = (40, 50, 50)
    ncells = len(cells)
    batchsize = 5000

    # get the convnet layers
    layers = convnet(stim_shape, ncells, num_filters=(8, 16),
                     filter_size=(13, 13), weight_init='normal', l2_reg=0.1)

    # compile the keras model
    model = sequential(layers, 'adam')

    # load experiment data
    test_stimuli = ['whitenoise', 'naturalscene']
    data = Experiment(exptdate, cells, train_stimuli, test_stimuli, stim_shape[0], batchsize)

    # create a monitor to track progress
    monitor = Monitor('convnet', model, data, readme, save_every=5)

    # train
    train(model, data, monitor, num_epochs=100)

    return model


if __name__ == '__main__':
    mdl = fit_convnet([0, 1, 2, 3, 4], ['naturalscene'], '15-10-07')
