import subprocess
import os
from json import loads
from json import dumps
from pprint import pprint as pp
import ast
import time
import sys
import re

class VolumeOperations(object):
    def __init__(self, **kwargs):
        for key,value in kwargs.iteritems():
            print "%s = %s" % (key,value)

    print "RRRRRR"

    def volumes_create(self):
        def __init__(bootable_factor, replication_factor, size):
            self.bootable_factor = bootable_factor
            self.replication_factor = replication_factor
            self.size = size
            print "Requested stuff are %s %s %s" %(self.bootable_factor,self.replication_factor,self.size)

