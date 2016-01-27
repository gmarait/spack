##############################################################################
# Copyright (c) 2013, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Written by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License (as published by
# the Free Software Foundation) version 2.1 dated February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os
import sys
import spack

class Cmake(Package):
    """A cross-platform, open-source build system. CMake is a family of
       tools designed to build, test and package software."""
    homepage  = 'https://www.cmake.org'

    version('2.8.10.2', '097278785da7182ec0aea8769d06860c',
            url = 'http://www.cmake.org/files/v2.8/cmake-2.8.10.2.tar.gz')

    version('3.0.2', 'db4c687a31444a929d2fdc36c4dfb95f',
            url = 'http://www.cmake.org/files/v3.0/cmake-3.0.2.tar.gz')

    version('3.4.0', 'cd3034e0a44256a0917e254167217fc8',
            url = 'https://cmake.org/files/v3.4/cmake-3.4.0.tar.gz')

#    version('3.0.1', 'e2e05d84cb44a42f1371d9995631dcf5')
#    version('3.0.0', '21a1c85e1a3b803c4b48e7ff915a863e')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        configure('--prefix='   + prefix,
                  '--parallel=' + str(make_jobs),
                  '--', '-DCMAKE_USE_OPENSSL=ON')
        make()
        make('install')

    # to use the existing version available in the environment: CMAKE_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('CMAKE_DIR'):
            cmakeroot=os.environ['CMAKE_DIR']
            if os.path.isdir(cmakeroot):
                os.symlink(cmakeroot+"/bin", prefix.bin)
                os.symlink(cmakeroot+"/share", prefix.share)
            else:
                sys.exit(cmakeroot+' directory does not exist.'+' Do you really have openmpi installed in '+cmakeroot+' ?')
        else:
            sys.exit('CMAKE_DIR is not set, you must set this environment variable to the installation path of your cmake')
