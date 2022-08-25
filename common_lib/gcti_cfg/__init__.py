import sys
import os
import imp
gcti_cfgDir = os.path.dirname(os.path.realpath(__file__))

print gcti_cfgDir
sys.path.append(gcti_cfgDir)

try:
    module_path = imp.find_module('enum')[1]
    for el in sys.path:
        if module_path == el + os.path.sep + "enum.py":
            sys.path.insert(sys.path.index(el), os.path.join(gcti_cfgDir, 'common'))
            break
except ImportError:
    sys.path.append(os.path.join(gcti_cfgDir, 'common'))


libPlatf = 'unknown'
if   sys.platform.find('win')   >= 0: libPlatf = 'lib.windows-x86'
elif sys.platform.find('linux') >= 0: libPlatf = 'lib.linux-x86_64'

libDir = (os.path.join(gcti_cfgDir, libPlatf + '-' + sys.version[0:3]))

if sys.maxunicode > 65535: libDir = libDir + '-UCS4'

if os.path.exists(libDir): sys.path.append(libDir)

import model_configserver
from   model_configserver import *
import default_servers
from   default_servers import SetDefaultServer

