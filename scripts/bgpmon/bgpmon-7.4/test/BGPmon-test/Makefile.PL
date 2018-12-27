use 5.010001;
use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.
WriteMakefile(
    NAME              => 'BGPmon::test',
    VERSION_FROM      => 'lib/BGPmon/test.pm', # finds $VERSION
    PREREQ_PM         => { File::ReadBackwards => 1.05,
                           Expect => 1.21}, # e.g., Module::Name => 1.1
    ($] >= 5.005 ?     ## Add these new keywords supported since 5.005
      (ABSTRACT_FROM  => 'lib/BGPmon/test.pm', # retrieve abstract from module
       AUTHOR         => 'Cathie Olschanowsky <cathie@>') : ()),
);
