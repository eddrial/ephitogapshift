'''
Created on 19 Jan 2022

@author: oqb
'''
import numpy as np

class UndulatorMotion(object):
    '''
    classdocs
    '''


    def __init__(self, Energy, Phase, Steps = 1, gap_shift_table = '../bin/ba_file.idt'):
        '''
        Constructor
        '''
        self.steps = Steps
        self.phase = Phase
        self.energy = Energy
        
        self.allowed_harmonics = 'exists'
        self.target_harmonic = 'exists'
        
        self.gap_shift_table_fname = gap_shift_table
        
        #self.breakpoint = 1
        
    def read_gap_shift_table(self):
        self.gap_shift_table = {}
        
        a = np.genfromtxt(self.gap_shift_table_fname)
        
        #for each line
        for line in a:
            if 'Harmonic {}'.format(int(line[4])) in self.gap_shift_table.keys():
                self.gap_shift_table['Harmonic {}'.format(int(line[4]))] = np.vstack([self.gap_shift_table['Harmonic {}'.format(int(line[4]))],line[:-1]])
            else:
                self.gap_shift_table['Harmonic {}'.format(int(line[4]))] = np.array(line[:-1])
        
        #check if dictionary entry exists
        #if exists, append data to table
        #else create dictionary entry and initialise table and set first line