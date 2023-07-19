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
    RULEBASED = 'RULEBASED'
    ECC = 'ECC'
    MLCBMAD = 'MLCBMAD'


class FingerprinterType(Enum):
    ENVIPATH_FINGERPRINTER = 'ENVIPATH_FINGERPRINTER'


class AssociationType(Enum):
    DATABASED = 'DATABASED'
    CALCULATED = 'CALCULATED'


class EvaluationType(Enum):
    SINGLE_GEN = 'single'
    MULTI_GEN = 'multigen'


class Permission(Enum):
    READ = 'read'
    WRITE = 'write'
    NONE = 'none'
