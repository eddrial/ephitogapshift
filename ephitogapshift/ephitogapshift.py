'''
Created on 19 Jan 2022

@author: oqb
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation,  CubicTriInterpolator, TriInterpolator, TriAnalyzer

class UndulatorMotion(object):
    '''
    classdocs
    '''


    def __init__(self, Energy, Phase, GSEP, Steps = 1):
        '''
        Constructor
        '''
        self.steps = np.array([Steps]).flatten()
        self.phase = np.array([Phase]).flatten()
        self.energy = np.array([Energy]).flatten()
        self.motion = {}
        self.GSEP = GSEP
        
        self.allowed_harmonics = np.array([])
        self.target_harmonic = 'exists'
        
        
        #self.breakpoint = 1
        
        
    def create_motion_trajectory(self):
        if (self.steps.__len__() == 1):
            if self.steps == 1: 
                if self.energy.__len__() == 1:
                    self.energy_steps = np.array([self.energy[0]]).flatten()
                else:
                    self.energy_steps = np.array([self.energy]).flatten()
                
                if self.phase.__len__() == 1:
                    self.phase_steps = np.array([self.phase[0]]).flatten()
                else:
                    self.phase_steps = np.array([self.phase]).flatten()
                
            elif self.steps > 1:
                if self.energy.__len__() > 1:
                    self.energy_steps = np.linspace(self.energy[0],self.energy[1],self.steps[0])
                else:
                    self.energy_steps = np.array([self.energy[0]]).flatten()
                    
                if self.phase.__len__() > 1:
                    self.phase_steps = np.linspace(self.phase[0],self.phase[1],self.steps[0])
                else:
                    self.phase_steps = np.array([self.phase[0]]).flatten()
        
        elif self.steps.__len__() == 2:
            self.energy_steps = np.linspace(self.energy[0],self.energy[1],self.steps[0])
            self.phase_steps = np.linspace(self.phase[0],self.phase[1],self.steps[1])
            
            self.energy_steps, self.phase_steps = np.meshgrid(self.energy_steps, self.phase_steps)
            
        else:
            self.energy_steps = np.array([self.energy]).flatten()
            self.phase_steps = self.phase([self.phase]).flatten()
            
            self.energy_steps, self.phase_steps = np.meshgrid(self.energy_steps, self.phase_steps)
            
        if len(self.energy_steps) == 1:
            self.energy_steps = np.full(len(self.phase_steps),self.energy_steps)
            
        elif len(self.phase_steps) == 1:
            self.phase_steps = np.full(len(self.energy_steps),self.phase_steps)
        
        
    def check_valid_motion(self):
        
        for harmonic in self.GSEP.gap_shift_table:
            #calculate gap and shift positions for energy-phase raster
            #en, ph = np.meshgrid(self.energy, self.phase)
            reqd_gaps = self.GSEP.inverse_lookup['{} Gap'.format(harmonic)](self.energy_steps, self.phase_steps)
            reqd_shifts = self.GSEP.inverse_lookup['{} Shift'.format(harmonic)](self.energy_steps, self.phase_steps)
                    
            if np.isnan(reqd_gaps.data).any() or np.isnan(reqd_shifts.data).any():
                pass
            else:
                self.allowed_harmonics = np.append(self.allowed_harmonics, int(harmonic[-1]))#append available harmonic
                #store gap/shift pairs
                self.motion[harmonic] = np.vstack((reqd_gaps.flatten(),reqd_shifts.flatten()))
                
                
    def save_motion_txt(self):
        #my_tab_header = ['#{%1s}{%10s}{%10s}{%10s}'.format('Energy', 'Poln', 'Gap', 'Shift')]
        
        enphase_table = np.vstack([self.energy_steps.flatten(), self.phase_steps.flatten()])
        for harmonic in self.allowed_harmonics:
            enphasegapshift_table = np.vstack([enphase_table,self.motion['Harmonic {}'.format(int(harmonic))]])
            np.savetxt('motiontst_Harmonic_{}.txt'.format(harmonic), enphasegapshift_table.T, fmt = ['%10.2f','%10.2f','%10.5f','%10.5f'])
    
class GapShiftEnergyPhase(object):
    
    def __init__(self, table_fname= '../bin/ba_file.idt'):
        self.gap_shift_table_fname = table_fname
        self.gap_shift_table = {}
        
        a = np.genfromtxt(self.gap_shift_table_fname)
        
        #for each line
        for line in a:
            if 'Harmonic {}'.format(int(line[4])) in self.gap_shift_table.keys():
                self.gap_shift_table['Harmonic {}'.format(int(line[4]))] = np.vstack([self.gap_shift_table['Harmonic {}'.format(int(line[4]))],line[:-1]])
            else:
                self.gap_shift_table['Harmonic {}'.format(int(line[4]))] = np.array(line[:-1])
                
    def create_inverse_lookups(self):
        self.inverse_lookup = {}
        
        for harmonic in self.gap_shift_table:
#            if (np.min(self.energy) > np.min(self.gap_shift_table[harmonic][:,2]) 
#                and np.max(self.energy) < np.max(self.gap_shift_table[harmonic][:,2])):
#                self.allowed_harmonics = np.append(self.allowed_harmonics,int(harmonic[-1]))
                
        #creating triangular grid, and interpolating (shift, gap)
            #grid creation *Grid is Energy Phase Grid*
            triObj = Triangulation(self.gap_shift_table[harmonic][:,2],self.gap_shift_table[harmonic][:,3])
            
            #masking z as in CubicTriInterpolator to work around an error
            #which is due to non-singular results (i.e. the last step in a table = the penultimate step trick)
            aa = TriInterpolator(triObj,self.gap_shift_table[harmonic][:,2])
            aa._triangulation.get_cpp_triangulation()
            tri_analyzer = TriAnalyzer(aa._triangulation)
            
            (compressed_triangles, compressed_x, compressed_y, tri_renum,
             node_renum) = tri_analyzer._get_compressed_triangulation(True, True)
             
            node_mask = (node_renum == -1)
            clean_triObj = Triangulation(self.gap_shift_table[harmonic][~node_mask,2],self.gap_shift_table[harmonic][~node_mask,3])
            #aa._z[node_renum[~node_mask]] = aa._z   
            #self._z = self._z[~node_mask]
            #cubic interpolation of Gap and Shift for Energy/Phase
            self.inverse_lookup['{} Gap'.format(harmonic)] = CubicTriInterpolator(clean_triObj,self.gap_shift_table[harmonic][~node_mask,0])
            self.inverse_lookup['{} Shift'.format(harmonic)] = CubicTriInterpolator(clean_triObj,self.gap_shift_table[harmonic][~node_mask,1])
