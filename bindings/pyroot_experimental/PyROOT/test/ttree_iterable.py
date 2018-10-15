import unittest
from array import array

import ROOT
from libcppyy import SetOwnership


class TTreeIterable(unittest.TestCase):
    """
    Test for the pythonization that makes TTree instances iterable in Python. 
    For example, this allows to do:
    `for event in mytree:`
         `...`

    Since this pythonization is common to TTree and its subclasses, TChain is
    also tested here.
    """

    filename  = 'treeiterable.root'
    treename  = 'mytree'
    nentries  = 10
    arraysize = 10
    more      = 10

    # Setup
    @classmethod
    def setUpClass(cls):
        ROOT.gInterpreter.Declare('#include "TreeHelper.h"')                                          
        ROOT.CreateTTree(cls.filename,
                         cls.treename,
                         cls.nentries,
                         cls.arraysize,
                         cls.more,
                         'RECREATE')

    # Helper
    def get_file_objects(self):
        f = ROOT.TFile(self.filename)
        t = f.Get(self.treename)
        # Prevent double deletion of the tree (Python and C++ TFile)
        SetOwnership(t, False)

        c = ROOT.TChain(self.treename)
        c.Add(self.filename)
        c.Add(self.filename)

        return f,t,c

    # Tests
    def test_basic_type_branch(self):
        f,t,c = self.get_file_objects()

        for ds in t,c:
            n = array('f', [ 0. ])
            ds.SetBranchAddress('floatb', n)

            i = 0
            for entry in ds:
                self.assertEqual(n[0], i+self.more)
                i = (i + 1) % self.nentries

    def test_array_branch(self):
        f,t,c = self.get_file_objects()

        for ds in t,c:
            a = array('d', self.arraysize*[ 0. ])
            ds.SetBranchAddress('arrayb', a)

            i = 0
            for entry in ds:
                for j in range(self.arraysize):
                    self.assertEqual(a[j], i+j)
                i = (i + 1) % self.nentries

    def test_struct_branch(self):
        f,t,c = self.get_file_objects()

        for ds in t,c:
            ms = ROOT.MyStruct()
            ds.SetBranchAddress('structleaflistb', ms)

            i = 0
            for entry in ds:
                self.assertEqual(ms.myint1, i+self.more)
                self.assertEqual(ms.myint2, i*self.more)
                i = (i + 1) % self.nentries


if __name__ == '__main__':
    unittest.main()