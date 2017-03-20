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

    def volumes_create(self):


    print "$$$$$$$"