# Before `make install' is performed this script should be runnable with
# `make test'. After `make install' it should work as `perl BGPmon-test.t'

#########################

# change 'tests => 1' to 'tests => last_test_to_print';

use Test::More;
BEGIN { use_ok('BGPmon::RoutingTable') };
use_ok('BGPmon::RoutingTable');
use_ok('BGPmon::MRT::BgpdumpReader');
my $call_count = 0;

#########################

my $table = BGPmon::RoutingTable->new;
my $reader = BGPmon::MRT::BgpdumpReader->new;
$reader->inputFile("t/test-bgpdump-input.txt");
$reader->handler(\&BGPmon::RoutingTable::addPrefixIfNew);
$reader->handlerParam($table);
$reader->readReverse(1);
ok($reader->read(), "read return value:  ");
my %prefix;
$prefix{timestamp} = "09/16/11 17:30:00";
$prefix{action} = "A";
$prefix{peerIP} = "209.123.12.51";
$prefix{peerAS} = "8001";
$prefix{prefix} = "173.244.87.0/24";
$prefix{pathAttrs} = "8001 11666 14500";
ok($table->prefixExists(%prefix));

my $table2 = BGPmon::RoutingTable->new;
my $reader2 = BGPmon::MRT::BgpdumpReader->new;
$reader2->inputFile("t/test-bgpdump-input.txt");
$reader2->handler(\&BGPmon::RoutingTable::addPrefixIfNew);
$reader2->handlerParam($table2);
$reader2->readReverse(1);
ok($reader2->read(), "read return value:  ");

ok($table->equivalentTo($table2));


done_testing();


