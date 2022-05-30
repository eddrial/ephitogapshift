'''
Created on 19 Jan 2022

@author: oqb
'''
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation,  CubicTriInterpolator, TriInterpolator, TriAnalyzer

import json
import pickle
import h5py as h5
from mpmath import harmonic

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
        self.reqd_gaps = {}
        self.reqd_shifts = {}
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
            self.reqd_gaps['{} Gap'.format(harmonic)] = self.GSEP.inverse_lookup['{} Gap'.format(harmonic)](self.energy_steps, self.phase_steps)
            self.reqd_shifts['{} Shift'.format(harmonic)] = self.GSEP.inverse_lookup['{} Shift'.format(harmonic)](self.energy_steps, self.phase_steps)
                    
            if np.isnan(self.reqd_gaps['{} Gap'.format(harmonic)].data).any() or np.isnan(self.reqd_shifts['{} Shift'.format(harmonic)].data).any():
                pass
            else:
                self.allowed_harmonics = np.append(self.allowed_harmonics, int(harmonic[-1]))#append available harmonic
                #store gap/shift pairs
                self.motion[harmonic] = np.vstack((self.reqd_gaps['{} Gap'.format(harmonic)].flatten(),self.reqd_shifts['{} Shift'.format(harmonic)].flatten()))
                
    
    def create_lookup_table(self):
        #I think this can be sliced together in a more intelligent way
        #table is [Energy, Polarisation, Polarisation Mode, Harmonic,Undulator Position(Gap,Shift)]
        all_harmonics = np.array([])
        
        for harmonic in self.GSEP.gap_shift_table:
            #nptst[3,:,:,:,2,:] = int(harmonic[9:])
            all_harmonics = np.append(all_harmonics, int(harmonic[9:]))
            
        self.lookup_table= np.meshgrid(self.energy_steps[0], self.phase_steps[:,0],np.linspace(0,1,1),all_harmonics,np.arange(5,7))
        self.lookup_table = np.array(self.lookup_table)
        
        for h in range(len(all_harmonics)):
            self.lookup_table[4,:,:,0,h,0]=self.reqd_gaps['Harmonic {} Gap'.format(int(self.lookup_table[3,0,0,0,h,0]))].data
            self.lookup_table[4,:,:,0,h,1]=self.reqd_shifts['Harmonic {} Shift'.format(int(self.lookup_table[3,0,0,0,h,0]))].data 
            
        #create lookup_dictionary
        self.lookup_dict = {}
        for mode in range(len(self.lookup_table[0,0,0,:,0,0])):
            self.lookup_dict[self.lookup_table[2,0,0,mode,0,0]] = {}
            for harmonic in range(len(self.lookup_table[0,0,0,0,:,0])):
                self.lookup_dict[self.lookup_table[2,0,0,mode,0,0]][self.lookup_table[3,0,0,mode,harmonic,0]] = {}
                for polarisation in range(len(self.lookup_table[0,:,0,0,0,0])):
                    self.lookup_dict[self.lookup_table[2,0,0,mode,0,0]][self.lookup_table[3,0,0,mode,harmonic,0]][self.lookup_table[1,polarisation,0,mode,harmonic,0]] = {}
                    for energy in range(len(self.lookup_table[0,0,:,0,0,0])):
                        self.lookup_dict[self.lookup_table[2,0,0,mode,0,0]][self.lookup_table[3,0,0,mode,harmonic,0]][self.lookup_table[1,polarisation,0,mode,harmonic,0]][self.lookup_table[0,polarisation,energy,mode,harmonic,0]] = self.lookup_table[4,polarisation,energy,mode,harmonic,:].tolist()
                        
                        
        
        
    
    def save_motion_txt(self):
        #my_tab_header = ['#{%1s}{%10s}{%10s}{%10s}'.format('Energy', 'Poln', 'Gap', 'Shift')]
        
        enphase_table = np.vstack([self.energy_steps.flatten(), self.phase_steps.flatten()])
        for harmonic in self.allowed_harmonics:
            enphasegapshift_table = np.vstack([enphase_table,self.motion['Harmonic {}'.format(int(harmonic))]])
            np.savetxt('motiontst_Harmonic_{}.txt'.format(harmonic), enphasegapshift_table.T, fmt = ['%10.2f','%10.2f','%10.5f','%10.5f'])
    
    def save_lookup_txt(self,mypath,myfname):
        np.savetxt('{}/{}.icv.txt'.format(mypath,myfname),self.lookup_table.flatten(), delimiter = '\t', newline = '\n', 
                   header = 'The correct array shape is \n{}\n[Axis, Energy, Polarisation, Polarisation Mode, Harmonic, Position [Gap, Shift]]'.format(str(self.lookup_table.shape)))
    
    def save_lookup_json(self, mypath, myfname):
        with open('{}/{}_list.json'.format(mypath,myfname), 'w') as file:
            json.dump(self.lookup_table.tolist(),file, indent = '\t')
            
        with open('{}/{}_dict.json'.format(mypath,myfname), 'w') as file:
            json.dump(self.lookup_dict,file, indent = '\t')
    
    def save_lookup_pickle(self, mypath, myfname):
        pickle.dump( self.lookup_table, open( '{}/{}_table.pkl'.format(mypath,myfname), "wb" ) )
        pickle.dump( self.lookup_dict, open( '{}/{}_dict.pkl'.format(mypath,myfname), "wb" ) )

    
    def save_lookup_h5(self, mypath, myfname):
        with h5.File('{}/{}.h5'.format(mypath, myfname), 'w') as h5f:
            
            und_table = h5f.create_dataset('undulator_table', data = self.lookup_table[4])
            
            energy = h5f.create_dataset('energy', data = self.lookup_table[0,0,:,0,0,0])
            energy.make_scale('energy')
            energy.attrs['units'] = 'eV'
            und_table.dims[1].label = 'Photon Energy'
            und_table.dims[1].attach_scale(energy)
            
            polarisation = h5f.create_dataset('polarisation', data = self.lookup_table[1,:,0,0,0,0])
            polarisation.make_scale('polarisation')
            polarisation.attrs['units'] = 'degrees'
            und_table.dims[0].label = 'Polarisation Angle'
            und_table.dims[0].attach_scale(polarisation)
            
            mode = h5f.create_dataset('mode', data = [s.encode() for s in ["Linear_Polarisation"]])
            mode.make_scale('mode')
            und_table.dims[2].label = 'Polarisation Mode'
            und_table.dims[2].attach_scale(mode)
            
            und_mode = h5f.create_dataset('undulator mode', data = [s.encode() for s in ["Anti_Parallel"]])
            und_mode.make_scale('undulator mode')
            und_table.dims[2].label = 'Undulator Mode'
            und_table.dims[2].attach_scale(und_mode)
            
            harmonic = h5f.create_dataset('harmonic', data = self.lookup_table[3,0,0,0,:,0])
            harmonic.make_scale('harmonic')
            und_table.dims[3].label = 'Harmonic'
            und_table.dims[3].attach_scale(harmonic)
            
            und_coords = h5f.create_dataset('undulator position', data = [s.encode() for s in ["Gap", "Shift"]])
            und_coords.make_scale('undulator position')
            und_table.dims[4].label = 'Undulator Position'
            und_table.dims[4].attach_scale(und_coords)
            
            
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
