'''
Created on Feb 12, 2014

@author: przemek
'''

from itertools import imap
import operator

class Network:
    def __init__(self, inputs, hidden, outputs):
        self.inputs = inputs
        self.hidden = hidden
        self.outputs = outputs
    
    def set_params(self, params):
        self.params = params
    
    def number_of_params(self):
        return (self.inputs + 1) * self.hidden + (self.hidden + 1) * self.outputs 
    
    def activate(self, inp):
        param_iterator = iter(self.params)
        hidden_layer_value = self._calculate_layer(inp, self.hidden, param_iterator)
        output = self._calculate_layer(hidden_layer_value, self.outputs, param_iterator)
        return output
    
    def _calculate_layer(self, previous, m, param_iterator):
        previous.append(1)
        
        return [self._calculate_neuron(previous, param_iterator) for _ in xrange(m)]
    
    def _calculate_neuron(self, previous_layer, param_iterator):
        return sum(imap(operator.mul, iter(previous_layer), param_iterator))