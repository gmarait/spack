from spack import *
import spack
import os
import shutil
import platform
from subprocess import call

class Actipoletd(Package):
    """
    A Finite Element Time Domain Acoustic Solver.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir  = spack.repo.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = "file:"+join_path(pkg_dir, "empty.tar.gz")

    try:
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'actipoletd.git', branch='master')
        version('1.7.0', git=repo+'actipoletd.git', tag='v1.7.0')
    except KeyError:
        pass

    version('src')
    version('devel', git="/Users/sylvand/local/actipoletd", branch='master')
    variant('shared', default=True, description='Build ACTIPOLETD as a shared library')

    depends_on("scab")
    depends_on("scab@src", when="@src")

    # Global variant NETLIB
    variant('netlib', default=False, description='Use all netlib libraries as dependencies')
    depends_on("netlib-blas", when="+netlib")
    depends_on("netlib-blacs", when="+netlib")
    depends_on("netlib-cblas", when="+netlib")
    depends_on("netlib-lapacke", when="+netlib")
    depends_on("netlib-lapack", when="+netlib")
    depends_on("netlib-scalapack", when="+netlib")
    # Global variant MKL
    variant('mkl', default=False, description='Use all MKL libraries as dependencies')
    depends_on("mkl-blas", when="+mkl")
    depends_on("mkl-scalapack", when="+mkl")

    if os.getenv("LOCAL_PATH"):
        project_local_path = os.environ["LOCAL_PATH"] + "/actipoletd"

    def install(self, spec, prefix):
        if self.spec.satisfies('@src') and os.path.exists('spack-build'):
            shutil.rmtree('spack-build')

        with working_dir('spack-build', create=True):

            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            # Option for invoking the assembler on OSX (for sse/avx intrinsics)
            opt_ass=" -Wa,-q" if platform.system() == "Darwin" else ""

            if spec.satisfies('%gcc'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug",
                                   "-DCMAKE_C_FLAGS=-fopenmp -D_GNU_SOURCE -pthread"+opt_ass,
                                   '-DCMAKE_C_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread'+opt_ass,
                                   '-DCMAKE_CXX_FLAGS=-pthread -fopenmp'+opt_ass,
                                   '-DCMAKE_CXX_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread'+opt_ass,
                                   '-DCMAKE_Fortran_FLAGS=-pthread -fopenmp',
                                   '-DCMAKE_Fortran_FLAGS_DEBUG=-g -fopenmp -pthread'])

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            scab = spec['scab'].prefix
            cmake_args.extend(["-DSCAB_DIR=%s/CMake" % scab.share])

            cmake(*cmake_args)

            make()
            make("install")
