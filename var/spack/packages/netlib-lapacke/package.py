from spack import *
import os
import platform
import spack

class NetlibLapacke(Package):
    """
    LAPACK version 3.X is a comprehensive FORTRAN library that does
    linear algebra operations including matrix inversions, least
    squared solutions to linear sets of equations, eigenvector
    analysis, singular value decomposition, etc. It is a very
    comprehensive and reputable package that has found extensive
    use in the scientific community.
    """
    homepage = "http://www.netlib.org/lapack/"

    version('3.6.0', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")
    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf',
            url="http://www.netlib.org/lapack/lapack-3.5.0.tgz")
    version('3.4.2', '61bf1a8a4469d4bdb7604f5897179478',
            url="http://www.netlib.org/lapack/lapack-3.4.2.tgz")
    version('3.4.1', '44c3869c38c8335c2b9c2a8bb276eb55',
            url="http://www.netlib.org/lapack/lapack-3.4.1.tgz")
    version('3.4.0', '02d5706ec03ba885fc246e5fa10d8c70',
            url="http://www.netlib.org/lapack/lapack-3.4.0.tgz")
    version('3.3.1', 'd0d533ec9a5b74933c2a1e84eedc58b4',
            url="http://www.netlib.org/lapack/lapack-3.3.1.tgz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('tmg', default=False, description="Build lapacke with tmg")
    variant('shared', default=True, description="Build shared library version")

    # virtual dependency
    provides('lapacke')

    # blas is a virtual dependency.
    depends_on('lapack')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-lapacke."""
        if os.path.isdir(spec.prefix.lib64):
            libdir = "lib64"
        if os.path.isdir(spec.prefix.lib):
            libdir = "lib"
        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                module.lapackelibname=[os.path.join(self.spec.prefix+"/%s", "liblapacke.dylib") % libdir]
            else:
                module.lapackelibname=[os.path.join(self.spec.prefix+"/%s", "liblapacke.so") % libdir]
        else:
            module.lapackelibname=[os.path.join(self.spec.prefix+"/%s", "liblapacke.a") % libdir]
        module.lapackelibfortname = module.lapackelibname

    def install(self, spec, prefix):

        cmake_args = ["."]
        cmake_args += std_cmake_args
        cmake_args += ["-Wno-dev"]
        cmake_args.extend([
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

        blas_libs = " ".join(blaslibfortname)
        blas_libs = blas_libs.replace(' ', ';')
        cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])

        lapack_libs = " ".join(lapacklibfortname)
        lapack_libs = lapack_libs.replace(' ', ';')
        cmake_args.extend(['-DLAPACK_LIBRARIES=%s' % lapack_libs])

        # Enable lapacke here.
        cmake_args.extend(["-DLAPACKE=ON"])
        if spec.satisfies('+tmg'):
            cmake_args.extend(["-DLAPACKE_WITH_TMG=ON"])
        else:
            cmake_args.extend(["-DLAPACKE_WITH_TMG=OFF"])
        cmake_args.extend(["-DBUILD_TESTING=OFF"])

        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
            if platform.system() == 'Darwin':
                cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')

        cmake(*cmake_args)
        make()
        make("install")

    # to use the existing version available in the environment: LAPACKE_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('LAPACKE_DIR'):
            netliblapackeroot=os.environ['LAPACKE_DIR']
            if os.path.isdir(netliblapackeroot):
                os.symlink(netliblapackeroot+"/bin", prefix.bin)
                os.symlink(netliblapackeroot+"/include", prefix.include)
                os.symlink(netliblapackeroot+"/lib", prefix.lib)
            else:
                sys.exit(netliblapackeroot+' directory does not exist.'+' Do you really have openmpi installed in '+netliblapackeroot+' ?')
        else:
            sys.exit('LAPACKE_DIR is not set, you must set this environment variable to the installation path of your netlib-lapacke')