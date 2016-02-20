"""
Toolbox with helpful utilities for exploring Keras models

"""

from __future__ import absolute_import, division, print_function
import numpy as np
import theano
import h5py
import os
import tableprint
from keras.models import model_from_json
from .experiments import loadexpt
from . import metrics


def load_model(model_path, weight_filename):
    """
    Loads a Keras model using:
    - an architecture.json file
    - an h5 weight file, for instance 'epoch018_iter01300_weights.h5'

    INPUT:
        model_path		the full path to the saved weight and architecture files, ending in '/'
        weight_filename	an h5 file with the weights
        OUTPUT:
        returns keras model
    """

    architecture_filename = 'architecture.json'
    with open(os.path.join(model_path, architecture_filename), 'r') as architecture_data:
        architecture_string = architecture_data.read()
        model = model_from_json(architecture_string)
        model.load_weights(os.path.join(model_path, weight_filename))

    return model


def load_partial_model(model, layer_id):
    """
    Returns the model up to a specified layer.

    INPUT:
        model       a keras model
        layer_id    an integer designating which layer is the new final layer

    OUTPUT:
        a theano function representing the partial model
    """

    # create theano function to generate activations of desired layer
    return theano.function([model.layers[0].input], model.layers[layer_id].get_output(train=False))


def list_layers(model_path, weight_filename):
    """
    Lists the layers in the model with their children.

    This provides an easy way to see how many "layers" in the model there are, and which ones
    have weights attached to them.

    Layers without weights and biases are relu, pool, or flatten layers.

    INPUT:
        model_path		the full path to the saved weight and architecture files, ending in '/'
        weight_filename	an h5 file with the weights

    OUTPUT:
        an ASCII table using tableprint
    """
    weights = h5py.File(model_path + weight_filename, 'r')
    layer_names = list(weights)

    # print header
    print(tableprint.hr(3))
    print(tableprint.header(['layer', 'weights', 'biases']))
    print(tableprint.hr(3))

    params = []
    for l in layer_names:
        params.append(list(weights[l]))
        if params[-1]:
            print(tableprint.row([l.encode('ascii', 'ignore'),
                  params[-1][0].encode('ascii', 'ignore'),
                  params[-1][1].encode('ascii', 'ignore')]))
        else:
            print(tableprint.row([l.encode('ascii', 'ignore'), '', '']))

    print(tableprint.hr(3))


def get_test_responses(model, stim_type='whitenoise', cells=[0], exptdate='15-10-07'):
    '''
        Get a list of [true_responses, model_responses] on the same test data.
    '''
    test_data = loadexpt(cells, stim_type, 'test', 40, exptdate=exptdate)

    truth = []
    predictions = []
    for X, y in datagen(50, *test_data, shuffle=False):
        truth.extend(y)
        predictions.extend(model.predict(X))

    truth = np.array(truth)
    predictions = np.array(predictions)

    return [truth, predictions]


def get_correlation(model, stim_type='natural', cells=[0], metric='cc'):
    """Get Pearson's r correlation."""
    truth, predictions = get_test_responses(model, stim_type=stim_type, cells=cells)

    metric_func = getattr(metrics, metric)

    test_cc = []
    for c in cells:
        test_cc.append(metric_func(truth[:, c], predictions[:, c]))

    return test_cc


def get_performance(model, stim_type='natural', cells=[0], metric='cc'):
    """
        Get correlation coefficient on held-out data for deep-retina.

        INPUT:
            model           Keras model
            stim_type       'natural' or 'white'; which test data to draw from?
            cells           list of cell indices
            metric          'cc' (scipy.stats.pearsonr),
                            'lli' (Log-likelihood improvement over a mean rate model in bits per spike),
                            'rmse' (Root mean squared error),
                            'fev' (Fraction of explained variance; note this does not take into account
                                    the variance from trial-to-trial)
    """
    truth, predictions = get_test_responses(model, stim_type=stim_type, cells=cells)

    # metric (function computing a score between true and predicted rates)
    metric_func = getattr(metrics, metric)

    # compute the test results
    test_results = [metric_func(truth[:, c], predictions[:, c]) for c in cells]

    return test_results


def get_weights(path_to_weights, layer_name='layer_0', weight_name='param_0'):
    """
    Return the weights from a saved .h5 file.

    INPUTS:
    path_to_weights path to weights
    layer_name      name of the layer you want
    weight_name     'param_0' or 'param_1' depending on if you want weights or biases
    """

    weight_file = h5py.File(path_to_weights, 'r')

    # param_0 stores the weights, param_1 stores biases
    weights = weight_file[layer_name][weight_name]
    return weights
