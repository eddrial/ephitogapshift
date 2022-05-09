'''
Created on 19 Jan 2022

@author: oqb
'''
import unittest
import numpy as np
from numpy import testing as npt
import ephitogapshift as epgs
from ephitogapshift import GapShiftEnergyPhase



class Test(unittest.TestCase):

    def assertHasAttr(self, obj, intendedAttr):
        testBool = hasattr(obj, intendedAttr)
    
        # python >=3.8 only, see below for older pythons
        self.assertTrue(testBool, msg='obj lacking an attribute. obj: {}, intendedAttr: {}'.format(obj, intendedAttr))

    @classmethod
    def setUpClass(cls):
        cls.gsep = GapShiftEnergyPhase()
        cls.gsep.create_inverse_lookups()
        
        cls.eg = epgs.UndulatorMotion(500,45,cls.gsep) #Single Point Case
        cls.eg.create_motion_trajectory()
        
        cls.eg1 = epgs.UndulatorMotion([500,510],30,cls.gsep,10) #scan energy
        cls.eg1.create_motion_trajectory()
        
        cls.egh = epgs.UndulatorMotion([500,510],0,cls.gsep,50) #scan energy H mode
        cls.egh.create_motion_trajectory()
        
        cls.egv = epgs.UndulatorMotion([500,510],90,cls.gsep,50) #scan energy V mode
        cls.egv.create_motion_trajectory()
        
        cls.eg600 = epgs.UndulatorMotion(600,[-45,45],cls.gsep,7) #scan phase at 607eV
        cls.eg600.create_motion_trajectory()
        
        cls.egarb = epgs.UndulatorMotion([600,610],[-20,5],cls.gsep,21)
        cls.egarb.create_motion_trajectory()
         
        cls.egraster = epgs.UndulatorMotion([600,610],[-45,45],cls.gsep,[11,5])
        cls.egraster.create_motion_trajectory()

    @classmethod
    def tearDown(cls):
        pass

#Check Object Attributes are created
    def testHasAttributeSteps(self):
        self.assertHasAttr(self.eg,"steps")
        
    def testHasAttributeEnergy(self):
        self.assertHasAttr(self.eg,"energy")
    
    def testHasAttributePhase(self):
        self.assertHasAttr(self.eg,"phase")
    
    def testHasAttributeAllowedHarmonics(self):
        self.assertHasAttr(self.eg,"allowed_harmonics")
    
    def testHasAttributeTargetHarmonic(self):
        self.assertHasAttr(self.eg,"target_harmonic")
        
    def testHasAttributeGap_shift_table_fname(self):
        self.assertHasAttr(self.eg, "GSEP")
    
    #Check Steps Parsing
    def testStepsIsOneByDefault(self):
        self.assertEqual(self.eg.steps, 1, 'Default Number Of Steps not 1')
    
    def testStepsParsing_FixedEnergyFixedPhase_Energy(self):
        npt.assert_array_equal(self.eg.energy_steps, np.array([500]),
                                'Motion Trajectory Calculation Fail: Energy Range, Fixed Phase')
        
    def testStepsParsing_FixedEnergyFixedPhase_Phase(self):
        npt.assert_array_equal(self.eg.phase_steps, np.array([45]).flatten(),
                                'Motion Trajectory Calculation Fail: Energy Range, Fixed Phase')
        
    def testStepsParsing_RangeEnergyFixedPhase_Energy(self):
        npt.assert_array_equal(self.eg1.energy_steps, np.linspace(500,510,10),
                                'Motion Trajectory Calculation Fail: Energy Range, Fixed Phase')
        
    def testStepsParsing_RangeEnergyFixedPhase_Phase(self):
        npt.assert_array_equal(self.eg1.phase_steps, np.array([30]).flatten(),
                                'Motion Trajectory Calculation Fail: Energy Range, Fixed Phase')
    
    def testStepsParsing_FixeedEnergyRangePhase_Energy(self):
        npt.assert_array_equal(self.eg600.energy_steps, np.array([600]),
                                'Motion Trajectory Calculation Fail: Energy Fixed, Phase Range')
        
    def testStepsParsing_FixedEnergyRangePhase_Phase(self):
        npt.assert_array_equal(self.eg600.phase_steps, np.linspace(-45,45,7).flatten(),
                                'Motion Trajectory Calculation Fail: Energy Fixed, Phase Range')
        
    def testStepsParsing_ArbitraryEnergyPhase_Energy(self):
        npt.assert_array_equal(self.egarb.energy_steps, np.linspace(600,610,21),
                                'Motion Trajectory Calculation Fail: Arbitrary Path')
        
    def testStepsParsing_ArbitraryEnergyPhase_Phase(self):
        npt.assert_array_equal(self.egarb.phase_steps, np.linspace(-20,5,21).flatten(),
                                'Motion Trajectory Calculation Fail: Arbitrary Path')
    
    def testStepsParsing_RasterEnergyPhase_Energy(self):
        npt.assert_array_equal(self.egraster.energy_steps, np.array([[600., 601., 602., 603., 604., 605., 606., 607., 608., 609., 610.],
                                                                  [600., 601., 602., 603., 604., 605., 606., 607., 608., 609., 610.],
                                                                  [600., 601., 602., 603., 604., 605., 606., 607., 608., 609., 610.],
                                                                  [600., 601., 602., 603., 604., 605., 606., 607., 608., 609., 610.],
                                                                  [600., 601., 602., 603., 604., 605., 606., 607., 608., 609., 610.]]),
                                'Motion Trajectory Calculation Fail: Rastered Path')
        
    def testStepsParsing_RasterEnergyPhase_Phase(self):
        npt.assert_array_equal(self.egraster.phase_steps, ([[-45. , -45. , -45. , -45. , -45. , -45. , -45. , -45. , -45. ,  -45. , -45. ],
                                                         [-22.5, -22.5, -22.5, -22.5, -22.5, -22.5, -22.5, -22.5, -22.5,  -22.5, -22.5],
                                                         [  0. ,   0. ,   0. ,   0. ,   0. ,   0. ,   0. ,   0. ,   0. ,  0. ,   0. ],
                                                         [ 22.5,  22.5,  22.5,  22.5,  22.5,  22.5,  22.5,  22.5,  22.5,  22.5,  22.5],
                                                         [ 45. ,  45. ,  45. ,  45. ,  45. ,  45. ,  45. ,  45. ,  45. ,  45. ,  45. ]]),
                                'Motion Trajectory Calculation Fail: Rastered Path')
    
            
    def testReadsGapShiftTableW(self):
        #self.eg.read_gap_shift_table()
        self.assertIn('Harmonic 1', self.gsep.gap_shift_table.keys(), 'input file is read incorrectly')
        self.assertIn('Harmonic 3', self.gsep.gap_shift_table.keys(),  'input file is read incorrectly')
        self.assertIn('Harmonic 5', self.gsep.gap_shift_table.keys(), 'input file is read incorrectly')
        
    def testReadGapShiftTableData(self):
        self.assertEqual(self.gsep.gap_shift_table['Harmonic 1'].__len__(), 8952, 'Input File reading incorrectly Harmonic 1')
        self.assertEqual(self.gsep.gap_shift_table['Harmonic 3'].__len__(), 16895, 'Input File reading incorrectly Harmonic 3')
        self.assertEqual(self.gsep.gap_shift_table['Harmonic 5'].__len__(), 18219, 'Input File reading incorrectly Harmonic 5')
        
    def testSimpleCheckValidMotion(self):
        self.eg.check_valid_motion()
        npt.assert_array_equal(self.eg.allowed_harmonics, np.array([1.,3.]))
        
    def testComplexCheckValidMotion(self):
        self.egraster.check_valid_motion()
        npt.assert_array_equal(self.egraster.allowed_harmonics, np.array([3.]))




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()