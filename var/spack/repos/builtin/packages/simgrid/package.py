from spack import *
import os
import spack

class Simgrid(Package):
    """To study the behavior of large-scale distributed systems such as Grids, Clouds, HPC or P2P systems."""
    homepage = "http://simgrid.gforge.inria.fr/index.html"
    url      = "http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz"

    version('3.15', 'e196d30e80350dce8cd41b0af468c4fc',
            url='https://gforge.inria.fr/frs/download.php/file/36621/SimGrid-3.15.tar.gz')
    version('3.14', 'dc80632250412d765d815164a25aac4a',
            url='https://gforge.inria.fr/frs/download.php/file/36382/SimGrid-3.14.tar.gz')
    version('3.13', '8ace1684972a01429d5f1c5db8966709',
            url='http://gforge.inria.fr/frs/download.php/file/35817/SimGrid-3.13.tar.gz')
    version('3.12', 'd73faaf81d7a9eb0d309cfd72532c5f1',
            url='http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz')
    version('3.11', '358ed81042bd283348604eb1beb80224',
            url='http://gforge.inria.fr/frs/download.php/file/33683/SimGrid-3.11.tar.gz')
    version('3.10', 'a345ad07e37539d54390f817b7271de7',
            url='http://gforge.inria.fr/frs/download.php/file/33124/SimGrid-3.10.tar.gz')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git')
    version('starpumpi', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git', branch='starpumpi')

    variant('doc', default=False, description='Enable building documentation')
    variant('smpi', default=True, description='SMPI provides MPI')
    variant('examples', default=False, description='Install examples')

    depends_on('cmake')

    def build(self, spec, prefix):
        make()
        make("install")

    def setup_dependent_package(self, module, dep_spec):
        if self.spec.satisfies('+smpi'):
            self.spec.smpicc  = join_path(self.prefix.bin, 'smpicc')
            self.spec.smpicxx = join_path(self.prefix.bin, 'smpicxx -std=c++11')
            self.spec.smpifc  = join_path(self.prefix.bin, 'smpif90')
            self.spec.smpif77 = join_path(self.prefix.bin, 'smpiff')

    def install(self, spec, prefix):
        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        if not spec.satisfies('+doc'):
            cmake_args.extend(["-Denable_documentation=OFF"])
        cmake(*cmake_args)
        self.build(spec,prefix)
        if spec.satisfies('+examples'):
            install_tree('examples', prefix + '/examples')
