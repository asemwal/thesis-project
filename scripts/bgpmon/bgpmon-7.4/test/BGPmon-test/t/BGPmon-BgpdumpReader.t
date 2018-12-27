# Before `make install' is performed this script should be runnable with
# `make test'. After `make install' it should work as `perl BGPmon-test.t'

#########################

# change 'tests => 1' to 'tests => last_test_to_print';

use Test::More;
BEGIN { use_ok('BGPmon::MRT::BgpdumpReader') };
use_ok('BGPmon::MRT::BgpdumpReader');
my $call_count = 0;

#########################
sub test_handler{
  my %info = @_;
  if($call_count == 0){
    ok($info{timestamp} eq "09/16/11 17:30:00","timestamp is " . $info{timestamp});
    ok($info{action} eq "A","action is ".$info{action});
    ok($info{peerIP} eq "209.123.12.51", "peer IP is " . $info{peerIP});
    ok($info{peerAS} eq "8001", "peerAS is " . $info{peerAS});
    ok($info{prefix} eq "173.244.87.0/24","prefix is ".$info{prefix});
    ok($info{pathAttrs} eq "8001 11666 14500","pathAttrs are " . $info{pathAttrs});
  }
  $call_count +=1;
}

my $reader = BGPmon::MRT::BgpdumpReader->new;
$reader->inputFile("t/test-bgpdump-input.txt");
$reader->handler(\&test_handler);
$reader->readReverse(1);
ok($reader->read(), "read return value:  ");
ok($call_count == 39,"right number of lines read $call_count");
# Insert your test code below, the Test::More module is use()ed here so read
# its man page ( perldoc Test::More ) for help writing this test script.
done_testing();


