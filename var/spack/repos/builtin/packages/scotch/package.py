from spack import *
import glob
import os
from subprocess import call
import subprocess
import sys
import spack
import platform
import gzip


def gunzip(file_name):
    inF = gzip.GzipFile(file_name, 'rb')
    s = inF.read()
    inF.close()

    print file_name[:-3]
    outF = file(file_name[:-3], 'wb')
    outF.write(s)
    outF.close()


class Scotch(Package):
    """Scotch is a software package for graph and mesh/hypergraph
       partitioning, graph clustering, and sparse matrix ordering."""
    homepage = "http://www.labri.fr/perso/pelegrin/scotch/"
    # url      = "http://gforge.inria.fr/frs/download.php/file/34099/scotch_6.0.3.tar.gz"
    list_url = "http://gforge.inria.fr/frs/?group_id=248"

    version('6.0.4', 'd58b825eb95e1db77efe8c6ff42d329f',
            url='https://gforge.inria.fr/frs/download.php/file/34618/scotch_6.0.4.tar.gz')
    version('6.0.3', '10b0cc0f184de2de99859eafaca83cfc',
            url='http://gforge.inria.fr/frs/download.php/file/34099/scotch_6.0.3.tar.gz')
    version('6.0.2b', '0da7429120177ca075ee0da248ffd7c2',
            url='https://gforge.inria.fr/frs/download.php/file/34089/scotch_6.0.2b.tar.gz')
    version('6.0.1', 'e22a664f66cfb2ddeab307245acc8f8c',
            url='https://gforge.inria.fr/frs/download.php/file/34078/scotch_6.0.1.tar.gz')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    variant('mpi', default=True, description='Activate the compilation of PT-Scotch')
    variant('pthread', default=True, description='Enable multithread with pthread')
    variant('compression', default=False, description='Activate the possibility to use compressed files')
    variant('esmumps', default=True, description='Activate the compilation of the lib esmumps needed by mumps')
    variant('shared', default=True, description='Build shared libraries')
    variant('idx64', default=False, description='to use 64 bits integers')
    variant('grf', default=False, description='Install grf examples files')

    depends_on('flex')
    depends_on('bison')
    depends_on('mpi', when='+mpi')
    depends_on('zlib', when='+compression')

    def compiler_specifics(self, makefile_inc, defines):

        spec = self.spec

        if self.compiler.name == 'gcc':
            defines.append('-Drestrict=__restrict')
        elif self.compiler.name == 'intel':
            defines.append('-restrict')

        makefile_inc.append('CCS       = cc')

        if spec.satisfies('+mpi'):
            makefile_inc.extend([
                    'CCP       = %s' % spec['mpi'].mpicc,
                    'CCD       = $(CCP)'
                    ])

        if not spec.satisfies('+mpi'):
            makefile_inc.extend([
                'CCP       = $(CCS)'
                'CCD       = $(CCS)'
                ])

    def library_build_type(self, makefile_inc, defines):
        makefile_inc.extend([
            'LIB       = .a',
            'CLIBFLAGS = ',
            'RANLIB    = ranlib',
            'AR        = ar',
            'ARFLAGS   = -ruv '
            ])

    @when('+shared')
    def library_build_type(self, makefile_inc, defines):
        if platform.system() == 'Darwin':
            libext = ".dylib"
            addarflags = "-undefined dynamic_lookup"
        else:
            libext = ".so"
            addarflags = ""
        makefile_inc.extend([
            'LIB       = %s' % libext,
            'CLIBFLAGS = -shared -fPIC',
            'RANLIB    = echo',
            'AR        = $(CC)',
            'ARFLAGS   = -shared $(LDFLAGS) %s -o' % addarflags
            ])

    def extra_features(self, makefile_inc, defines):
        spec = self.spec
        ldflags = []

        if '+compression' in spec:
            defines.append('-DCOMMON_FILE_COMPRESS_GZ')
            ldflags.append('-L%s -lz' % (spec['zlib'].prefix.lib))

        if spec.satisfies('+pthread'):
            defines.append('-DCOMMON_PTHREAD')
            defines.append('-DCOMMON_PTHREAD_BARRIER')

        if spec.satisfies('+idx64'):
            defines.append('-DINTSIZE64')
            defines.append('-DIDXSIZE64')

        if platform.system() == 'Darwin':
            ldflags.append('-lm -pthread')
        else:
            ldflags.append('-lm -lrt -pthread')

        makefile_inc.append('LDFLAGS   = %s' % ' '.join(ldflags))

    def setup(self):

        spec = self.spec

        if spec.satisfies('~pthread') and spec.satisfies('@6.0.4'):
            raise RuntimeError('Error: SCOTCH 6.0.4 cannot compile without pthread... :(')

        makefile_inc = []
        defines = [
            '-DCOMMON_TIMING_OLD',
            '-DCOMMON_RANDOM_FIXED_SEED',
            '-DSCOTCH_DETERMINISTIC',
            '-DSCOTCH_RENAME'
            ]

        self.library_build_type(makefile_inc, defines)
        self.compiler_specifics(makefile_inc, defines)
        self.extra_features(makefile_inc, defines)

        makefile_inc.extend([
            'EXE       =',
            'OBJ       = .o',
            'MAKE      = make',
            'CAT       = cat',
            'LN        = ln',
            'MKDIR     = mkdir',
            'MV        = mv',
            'CP        = cp',
            'CFLAGS    = -O3 %s' % (' '.join(defines)),
            'LEX       = %s -Pscotchyy -olex.yy.c' % os.path.join(spec['flex'].prefix.bin , 'flex'),
            'YACC      = %s -pscotchyy -y -b y' %    os.path.join(spec['bison'].prefix.bin, 'bison'),
            'prefix    = %s' % self.prefix,
            ''
            ])

        with working_dir('src'):
            with open('Makefile.inc', 'w') as fh:
                fh.write('\n'.join(makefile_inc))

    def install(self, spec, prefix):
        self.setup()

        targets = ['scotch']
        if spec.satisfies('+mpi'):
            targets.append('ptscotch')

        if spec.satisfies('+esmumps'):
            targets.append('esmumps')
            if spec.satisfies('+mpi'):
                targets.append('ptesmumps')

        with working_dir('src'):
            for app in targets:
                make(app, parallel=0)
            make('prefix=%s' % prefix, 'install')
            # esmumps libs are not installed by default (is it a mistake?)
            if spec.satisfies('+shared'):
                if platform.system() == 'Darwin':
                    libext = ".dylib"
                else:
                    libext = ".so"
            else:
                libext = ".a"
            if spec.satisfies('+esmumps'):
                install('../include/esmumps.h',   prefix.include)
                install('../lib/libesmumps%s' % libext,   prefix.lib)
                if spec.satisfies('+mpi'):
                    install('../lib/libptesmumps%s' % libext, prefix.lib)

        if spec.satisfies('+grf'):
            with working_dir('grf'):
                for f in os.listdir('.'):
                    gunzip(f)
            install_tree('grf', prefix + '/grf')

    # to use the existing version available in the environment: SCOTCH_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        install_tree("bin", prefix.bin)
        install_tree("include", prefix.include)
        install_tree("lib", prefix.lib)

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for Scotch."""
        spec = self.spec
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
        else:
            libext=".a"
        libdir = spec.prefix.lib

        scotchlibname=os.path.join(libdir, "libscotch%s") % libext
        scotcherrlibname=os.path.join(libdir, "libscotcherr%s") % libext
        scotcherrexitlibname=os.path.join(libdir, "libscotcherrexit%s") % libext
        ptscotchlibname=os.path.join(libdir, "libptscotch%s") % libext
        ptscotcherrlibname=os.path.join(libdir, "libptscotcherr%s") % libext
        ptscotcherrexitlibname=os.path.join(libdir, "libptscotcherrexit%s") % libext
        esmumpslibname=os.path.join(libdir, "libesmumps%s") % libext
        ptesmumpslibname=os.path.join(libdir, "libptesmumps%s") % libext

        otherlibs=' -lm'
        if spec.satisfies('+pthread'):
            otherlibs+=' -lpthread'
        if spec.satisfies('+compression'):
            otherlibs+=' -lz'
        if platform.system() == 'Linux':
            otherlibs+=' -lrt'

        spec.cc_link = '-L%s' % libdir
        if spec.satisfies('+esmumps'):
            if spec.satisfies('+mpi'):
                spec.cc_link+=' -lptesmumps'
                spec.cc_link+=' -lptscotch'
                spec.cc_link+=' -lptscotcherr'
        else:
            if spec.satisfies('+mpi'):
                spec.cc_link+=' -lptscotch'
                spec.cc_link+=' -lptscotcherr'
        if spec.satisfies('+esmumps'):
            spec.cc_link+=' -lesmumps'
        spec.cc_link+=' -lscotch'
        spec.cc_link+=' -lscotcherr'
        spec.cc_link+=otherlibs
