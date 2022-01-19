'''
Created on 19 Jan 2022

@author: oqb
'''
import unittest
import ephitogapshift as epgs



class Test(unittest.TestCase):

    def assertHasAttr(self, obj, intendedAttr):
        testBool = hasattr(obj, intendedAttr)
    
        # python >=3.8 only, see below for older pythons
        self.assertTrue(testBool, msg='obj lacking an attribute. obj: {}, intendedAttr: {}'.format(obj, intendedAttr))

    def setUp(self):
        self.eg = epgs.UndulatorMotion(500,45) #Single Point Case
        self.eg1 = epgs.UndulatorMotion([500,510],30,10) #scan energy
        self.egh = epgs.UndulatorMotion([500,510],0,50) #scan energy H mode
        self.egv = epgs.UndulatorMotion([500,510],90,50) #scan energy V mode
        self.eg600 = epgs.UndulatorMotion(607,[-45,45],0) #scan phase at 607eV
        self.egarb = epgs.UndulatorMotion([600,610],[-20,5],21) 
        self.egraster = epgs.UndulatorMotion([600,610],[-45,45],[11,5])
        


    def tearDown(self):
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
        
        
    #Check Steps Parsing
    def testStepsIsOneByDefault(self):
        self.assertEqual(self.eg.steps, 1, 'Default Number Of Steps not 1')
        
    def testStepsIsInteger(self):
        self.assertIsInstance(type(self.eg.steps), int, 'Number of steps is non-integer')
        




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()