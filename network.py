'''
Created on Feb 12, 2014

@author: przemek
'''

class Network:
    def __init__(self, inputs, hidden, outputs):
        self.inputs = inputs
        self.hidden = hidden
        self.outputs = outputs
    
    def set_params(self, params):
        self.params = params
    
    def activate(self, input):
        hidden_layer_value, param_shift = self._calculate_layer(input, self.hidden, 0)
        output, _ = self._calculate_layer(hidden_layer_value, self.outputs, param_shift)
        return output
    
    def _calculate_layer(self, previous, m, param_shift):
        previous.append(1)
        previous_layer_len = len(previous)
        
        values = []
        for _ in xrange(m):
            value = 0
            for j in xrange(previous_layer_len):
                value += previous[j] * self.params[param_shift]
                param_shift += 1
            values.append(value)
        
        return values, param_shift
    
n = Network(2, 2, 1)
n.set_params([1, 2, 3, 4, 5, 6, 7, 8, 9])
assert n.activate([10, 11])[0] == 1062 