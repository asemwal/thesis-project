# Before `make install' is performed this script should be runnable with
# `make test'. After `make install' it should work as `perl BGPmon-test.t'

#########################

# change 'tests => 1' to 'tests => last_test_to_print';

use Test::More;
BEGIN { use_ok('BGPmon::CLI::ShowBGPRoutes') };
use_ok('BGPmon::CLI::ShowBGPRoutes');
my $call_count = 0;

#########################
sub test_handler{
  my %info = @_;
  $call_count +=1;
}

my $reader = BGPmon::CLI::ShowBGPRoutes->new();
$reader->handler(\&test_handler);
ok($reader->read(), "read return value:  ");

done_testing();


