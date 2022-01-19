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
        self.eg = epgs.UndulatorMotion()


    def tearDown(self):
        pass


    def testHasAttributeSteps(self):
        self.assertHasAttr(self.eg,"steps")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()