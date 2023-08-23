# Copyright 2023 enviPath UG & Co. KG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from enum import Enum


class Endpoint(Enum):
    """
    Base class that defines all the available endpoints
    """
    USER = 'user'
    PACKAGE = 'package'
    COMPOUND = 'compound'
    PATHWAY = 'pathway'
    REACTION = 'reaction'
    RULE = 'rule'
    SIMPLERULE = 'simple-rule'
    SEQUENTIALCOMPOSITERULE = 'sequential-rule'
    PARALLELCOMPOSITERULE = 'parallel-rule'
    SCENARIO = 'scenario'
    SETTING = 'setting'
    GROUP = 'group'
    COMPOUNDSTRUCTURE = 'structure'
    NODE = 'node'
    EDGE = 'edge'
    RELATIVEREASONING = 'relative-reasoning'


class ClassifierType(Enum):
    """
    Base class that defines the types of available classifiers
    """
    RULEBASED = 'RULEBASED'
    ECC = 'ECC'
    MLCBMAD = 'MLCBMAD'


class FingerprinterType(Enum):
    """
    Class that stores the fingerprinter
    """
    ENVIPATH_FINGERPRINTER = 'ENVIPATH_FINGERPRINTER'


class AssociationType(Enum):
    """
    Class that stores the types of association
    """
    DATABASED = 'DATABASED'
    CALCULATED = 'CALCULATED'


class EvaluationType(Enum):
    """
    Class that stores the type of evaluation
    """
    SINGLE_GEN = 'single'
    MULTI_GEN = 'multigen'


class Permission(Enum):
    """
    Class that stores the permissions that can be granted
    """
    READ = 'read'
    WRITE = 'write'
    NONE = 'none'
