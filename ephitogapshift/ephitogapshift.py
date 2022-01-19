'''
Created on 19 Jan 2022

@author: oqb
'''

class UndulatorMotion(object):
    '''
    classdocs
    '''


    def __init__(self, Energy, Phase, Steps = 1):
        '''
        Constructor
        '''
        self.steps = Steps
        self.phase = Phase
        self.energy = Energy
        
        self.allowed_harmonics = 'exists'
        self.target_harmonic = 'exists'