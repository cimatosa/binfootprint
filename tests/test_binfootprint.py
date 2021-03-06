#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function

import sys
from os.path import abspath, dirname, split
# Add parent directory to beginning of path variable
sys.path = [split(dirname(abspath(__file__)))[0]] + sys.path

import binfootprint as bfp

import numpy as np
from collections import namedtuple
import pytest

import warnings
warnings.filterwarnings('error')

def test_version_tag():
    ob = 5
    binob = bfp.dump(ob)
    assert bfp.byte_to_ord(binob[0]) == bfp.getVersion()

def test_atom():
    atoms = [12345678, 3.141, 'hallo Welt', 'öäüß', True, False, None, 2**65, -3**65, b'\xff\fe\03', bytes(range(256))]

    # new version
    for atom in atoms:
        bin_atom = bfp.dump(atom)
        atom_prime = bfp.load(bin_atom)
        bin_ob_prime = bfp.dump(atom_prime)
        assert bin_atom == bin_ob_prime
        
        hash(bin_atom)

    # old version
    for atom in atoms:
        bin_atom = bfp.dump(atom, vers=0)
        atom_prime = bfp.load(bin_atom)
        bin_ob_prime = bfp.dump(atom_prime, vers=0)
        assert bin_atom == bin_ob_prime

        hash(bin_atom)
        
def test_tuple():
    t = (12345678, 3.141, 'hallo Welt', 'öäüß', True, False, None, (3, tuple(), (4,5,None), 'test'))
    bin_tuple = bfp.dump(t)
    assert type(bin_tuple) is bfp.BIN_TYPE
    t_prime = bfp.load(bin_tuple)
    assert t == t_prime
    bin_ob_prime = bfp.dump(t_prime)
    assert bin_tuple == bin_ob_prime

    # old version
    bin_tuple_00 = bfp.dump(t, vers=0)
    assert type(bin_tuple_00) is bfp.BIN_TYPE
    t_prime_00 = bfp.load(bin_tuple_00)
    assert t == t_prime_00
    
def test_nparray():
    ob = np.random.randn(3,53,2)
    bin_ob = bfp.dump(ob)
    assert type(bin_ob) is bfp.BIN_TYPE
    ob_prime = bfp.load(bin_ob)
    assert np.all(ob == ob_prime)
    bin_ob_prime = bfp.dump(ob_prime)
    assert bin_ob == bin_ob_prime
    
    ob = np.random.randn(3,53,2)
    ob = (ob, ob, 4, None)
    bin_ob = bfp.dump(ob)
    ob_prime = bfp.load(bin_ob)
    assert np.all(ob[0] == ob_prime[0])       
    assert np.all(ob[1] == ob_prime[1])
    bin_ob_prime = bfp.dump(ob_prime)
    assert bin_ob == bin_ob_prime

    # old version
    ob = np.random.randn(3,53,2)
    bin_ob_00 = bfp.dump(ob, vers=0)
    assert type(bin_ob_00) is bfp.BIN_TYPE
    ob_prime_00 = bfp.load(bin_ob_00)
    assert np.all(ob == ob_prime_00)

def test_list():
    ob = [1,2,3]
    bin_ob = bfp.dump(ob)
    assert type(bin_ob) is bfp.BIN_TYPE
    ob_prime = bfp.load(bin_ob)
    assert np.all(ob == ob_prime)
    bin_ob_prime = bfp.dump(ob_prime)
    assert bin_ob == bin_ob_prime
    
    ob = [1, (2,3), np.array([2j,3j])]
    bin_ob = bfp.dump(ob)
    ob_prime = bfp.load(bin_ob)
    bin_ob_prime = bfp.dump(ob_prime)
    assert bin_ob == bin_ob_prime
    
    assert np.all(ob[0] == ob_prime[0])
    assert np.all(ob[1] == ob_prime[1])
    assert np.all(ob[2] == ob_prime[2])

    # old version
    ob = [1,2,3]
    bin_ob_00 = bfp.dump(ob, vers=0)
    assert type(bin_ob_00) is bfp.BIN_TYPE
    ob_prime_00 = bfp.load(bin_ob_00)
    assert np.all(ob == ob_prime_00)
    
def test_getstate():
    class T(object):
        def __init__(self, a):
            self.a = a
        def __getstate__(self):
            return [self.a]
        def __setstate__(self, state):
            self.a = state[0]
    
    ob = T(4)
    bin_ob = bfp.dump(ob)
    assert type(bin_ob) is bfp.BIN_TYPE
    
    classes = {}
    classes['T'] = T
    
    ob_prime = bfp.load(bin_ob, classes)
    
    assert np.all(ob.a == ob_prime.a)
    bin_ob_prime = bfp.dump(ob_prime)
    assert bin_ob == bin_ob_prime
    
    try:
        ob_prime = bfp.load(bin_ob)
    except bfp.BFUnkownClassError:
        pass
    else:
        assert False, "binfootprint.BFUnkownClassError should have been raised"

    # old version
    bin_ob_00 = bfp.dump(ob, vers=0)
    assert type(bin_ob_00) is bfp.BIN_TYPE
    ob_prime_00 = bfp.load(bin_ob_00, classes)
    assert np.all(ob.a == ob_prime_00.a)

def test_named_tuple():
    obj_type = namedtuple('obj_type', ['a','b','c'])
    
    obj = obj_type(12345678, 3.141, 'hallo Welt')
    
    bin_obj = bfp.dump(obj)
    assert type(bin_obj) is bfp.BIN_TYPE
    obj_prime = bfp.load(bin_obj)   
    assert obj_prime.__class__.__name__ == obj.__class__.__name__
    assert obj_prime._fields == obj._fields
    assert obj_prime == obj
    bin_ob_prime = bfp.dump(obj_prime)
    assert bin_obj == bin_ob_prime
    
def test_complex():
    z = 3+4j
    bf = bfp.dump(z)
    assert type(bf) is bfp.BIN_TYPE
    zr = bfp.load(bf)
    assert zr == z

    # old version
    bf_00 = bfp.dump(z, vers=0)
    assert type(bf_00) is bfp.BIN_TYPE
    zr_00 = bfp.load(bf_00)
    assert zr_00 == z
    
def test_dict():
    a = {'a':1, 5:5, 3+4j:'l', False: b'ab4+#'}
    bf = bfp.dump(a)
    assert type(bf) is bfp.BIN_TYPE
    a_restored = bfp.load(bf)    
    for k in a:
        assert a[k] == a_restored[k]

    # old version
    bf_00 = bfp.dump(a, vers=0)
    assert type(bf_00) is bfp.BIN_TYPE
    a_restored_00 = bfp.load(bf_00)
    for k in a:
        assert a[k] == a_restored_00[k]

def test_versions():
    nt = namedtuple('nt', ['x', 'y'])
    n = nt(4,5)
    n2 = nt(n, n)
    ob = [3, n, n2]
    
    binob = bfp.dump(ob, vers = 0)
    # version 00 needs to explicitly know the namedtuple class
    ob_prime = bfp.load(binob, classes={'nt': nt})
    assert ob_prime == ob

    try:
        # if the namedtuple class is not passed raises BFUnknownClassError
        bfp.load(binob)
    except bfp.BFUnkownClassError:
        pass
    else:
        assert False, "binfootprint.BFUnkownClassError should have been raised"

    # thats how it works in the new version
    binob = bfp.dump(ob, vers = 0x80)
    rest_ob = bfp.load(binob)
    assert rest_ob == ob

def test_unsopportedtype():
    obj = bytearray([4,5,6])
    try:
        bfp.dump(obj)
    except TypeError:
        pass

      
     
if __name__ == "__main__":
    test_version_tag()
    test_atom()
    test_tuple()
    test_nparray()
    test_list()
    test_getstate()
    test_named_tuple()
    test_complex()
    test_dict()
    test_versions()
    test_unsopportedtype()


