from spack import *
import os
import spack
import sys

class Cuda(Package):
    """Nvidia CUDA/cuBLAS routines"""
    homepage = "https://developer.nvidia.com/cuda-zone"

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        if os.getenv('CUDA_DIR'):
            cudaroot=os.environ['CUDA_DIR']
            if os.path.isdir(cudaroot):
                os.symlink(cudaroot+"/bin", prefix.bin)
                os.symlink(cudaroot+"/include", prefix.include)
                os.symlink(cudaroot+"/lib64", prefix.lib)
            else:
                sys.exit(cudaroot+' directory does not exist.'+' Do you really have Nvidia CUDA installed in '+cudaroot+' ?')
        else:
            sys.exit('CUDA_DIR environment variable does not exist. Please set CUDA_DIR to use Nvidia CUDA')
