from spack import *
import os
import platform
import spack

class EigenBlas(Package):
    """Eigen BLAS"""
    homepage = "http://eigen.tuxfamily.org/index.php?title=Main_Page"

    version('3.3-rc1', '4ad437f8b77827a3e1271210c2a9468b',
            url = "http://bitbucket.org/eigen/eigen/get/3.3-rc1.tar.bz2")
    version('3.3-beta2', '109d4ae021e5f7143651850370659c0d',
            url = "http://bitbucket.org/eigen/eigen/get/3.3-beta2.tar.bz2")
    version('3.2.9', 'de11bfbfe2fd2dc4b32e8f416f58ee98',
            url = "http://bitbucket.org/eigen/eigen/get/3.2.9.tar.bz2")
    version('3.2.7', 'cc1bacbad97558b97da6b77c9644f184',
            url = "http://bitbucket.org/eigen/eigen/get/3.2.7.tar.bz2")
    version('hg-default', hg='https://bitbucket.org/eigen/eigen/')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    # virtual dependency
    provides('blas')

    variant('shared', default=True, description='Build Eigen BLAS as a shared library')
    variant('opti',   default=True, description='Build Eigen BLAS with optimization compiler flags')

    depends_on('cmake@3:')

    def install(self, spec, prefix):

        # configure and build process
        with working_dir('spack-build', create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DEIGEN_TEST_NOQT=ON"])
            cmake_args.extend(["-DEIGEN_TEST_NO_OPENGL=ON"])

            if spec.satisfies('+opti'):
                # Option for invoking the assembler on OSX (for sse/avx intrinsics)
                opt_ass=" -Wa,-q" if platform.system() == "Darwin" else ""
                if (spec.satisfies('@3.3:') or spec.satisfies('@hg-default')) and not spec.satisfies("arch=ppc64"):
                    cmake_args.extend(["-DCMAKE_CXX_FLAGS=-march=native"+opt_ass])
                if spec.satisfies("%xl"):
                    cmake_args.extend(["-DCMAKE_CXX_FLAGS=-O3 -qpic -qhot -qtune=auto -qarch=auto"])
                    cmake_args.extend(["-DCMAKE_C_FLAGS=-O3 -qpic -qhot -qtune=auto -qarch=auto"])
                    cmake_args.extend(["-DCMAKE_Fortran_FLAGS=-O3 -qpic -qhot -qtune=auto -qarch=auto"])

            cmake(*cmake_args)
            make('blas')

        # installation process
        # we copy the library: blas is a subproject of eigen, there is no specific rule to install blas solely
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
            eigenblaslibname="libeigen_blas%s" % libext
        else:
            libext=".a"
            eigenblaslibname="libeigen_blas_static.a"
        blaslibname="libeigen_blas%s" % libext
        mkdirp('%s/lib'%prefix)
        install('spack-build/blas/%s'%eigenblaslibname, '%s/lib/%s'%(prefix, blaslibname))

    # to use the existing version available in the environment: BLAS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BLAS_DIR'):
            eigenblasroot=os.environ['BLAS_DIR']
            if os.path.isdir(eigenblasroot):
                os.symlink(eigenblasroot+"/bin", prefix.bin)
                os.symlink(eigenblasroot+"/include", prefix.include)
                os.symlink(eigenblasroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(eigenblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+eigenblasroot+' ?')
        else:
            raise RuntimeError('BLAS_DIR is not set, you must set this environment variable to the installation path of your eigenblas')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for eigen-blas."""
        self.spec.cc_link="-L%s -leigen_blas" % self.spec.prefix.lib
        self.spec.fc_link="-L%s -leigen_blas" % self.spec.prefix.lib
