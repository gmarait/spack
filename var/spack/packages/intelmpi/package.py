from spack import *
import os
import spack
import sys

class Intelmpi(Package):
    """Intel's implementation of the
       the Message Passing Interface (MPI) standard."""
    homepage = "https://software.intel.com/en-us/intel-mpi-library"

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('I_MPI_ROOT'):
        mpiroot=os.environ['I_MPI_ROOT']
        if os.path.isdir(mpiroot):
            provides('mpi')

    def setup_dependent_environment(self, module, spec, dep_spec):
        bin = self.prefix.bin
        if spec.satisfies('%intel'):
            module.binmpicc  = os.path.join(bin, 'mpiicc')
            module.binmpicxx = os.path.join(bin, 'mpiicpc')
            module.binmpif77 = os.path.join(bin, 'mpiifort')
            module.binmpif90 = os.path.join(bin, 'mpiifort')
        else:
            module.binmpicc  = os.path.join(bin, 'mpicc')
            module.binmpicxx = os.path.join(bin, 'mpicxx')
            module.binmpif77 = os.path.join(bin, 'mpif77')
            module.binmpif90 = os.path.join(bin, 'mpif90')

    def install(self, spec, prefix):
        mpiroot=os.environ['I_MPI_ROOT']
        if os.path.isdir(mpiroot):
            os.symlink(mpiroot+"/intel64/bin", prefix.bin)
            os.symlink(mpiroot+"/intel64/etc", prefix.etc)
            os.symlink(mpiroot+"/intel64/include", prefix.include)
            os.symlink(mpiroot+"/intel64/lib", prefix.lib)
        else:
            sys.exit(mpiroot+' directory does not exist.'+' Do you really have intelmpi installed in '+mpiroot+' ?')
