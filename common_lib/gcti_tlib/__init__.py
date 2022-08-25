import sys
import os
gcti_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(gcti_dir)
sys.path.append(os.path.join(gcti_dir, 'common'))

libPlatf = 'unknown'
if   sys.platform.find('win')   >= 0: libPlatf = 'lib.windows-x86'
elif sys.platform.find('linux') >= 0: libPlatf = 'lib.linux-x86_64'

libDir = (os.path.join(gcti_dir, libPlatf + '-' + sys.version[0:3]))

if sys.maxunicode > 65535: libDir = libDir + '-UCS4'

if os.path.exists(libDir): sys.path.append(libDir)


