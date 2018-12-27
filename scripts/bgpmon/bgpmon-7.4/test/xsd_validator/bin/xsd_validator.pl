#!/usr/bin/perl
use warnings;
use strict;
use BGPmon::Fetch2 qw(connect_bgpdata read_xml_message close_connection is_connected);


my $xsdFileLoc = "../../../etc/bgp_monitor.xsd";

my $argLen = scalar(@ARGV);
if($argLen < 2){
	print "You must specify a host and port\n";
	print "perl xsd_validator.pl <hostname> <port>\n";
	exit 1;
}



my $server = $ARGV[0];
my $port = $ARGV[1];

my $schema = XML::LibXML::Schema->new(location => $xsdFileLoc);
my $parser = XML::LibXML->new;

# Connecting to BGPmon
print "Connecting to BGPmon\n";
my $retVal = connect_bgpdata($server, $port);
if($retVal != 0){
	print "Coudln't connect to $server:$port\n";
	exit 1;
}
print "Connected to BGPmon\n";

while(is_connected()){

	my $xmlmsg = read_xml_message();
	my $doc    = $parser->parse_string($xmlmsg);
	eval { $schema->validate($doc) };
	print "$xmlmsg\n$@\n\n" if $@;
	#print "." if not $@;
}
