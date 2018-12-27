#!/usr/bin/perl

use warnings; 
use strict; 
use Getopt::Long;

sub usage()
{
  print STDERR << "EOF";

  MRT Analyzer tool
  usage: $0 [-h] [-f file] [-d outputdir]
	    -f file      : specify MRT file
	    -d outputdir : print route data to directory
	    -h           : show help usage

  example: $0 -f ~Development/bgpmon-dev/test/mrt_harness/etc/updates.20110916.1715 -d ~Development/bgpmon-dev/test/mrt_harness/data 

EOF
 exit;
}

# setup defaults
my $filelocation = "/home/bgpmoner/Development/bgpmon-dev/test/mrt_harness/etc/updates.20110916.1715";
my $datadir = "/home/bgpmoner/Development/bgpmon-dev/test/mrt_harness/data";
my $help = 0;
my $bgpdumplocation = "/usr/local/sbin/bgpdump";

GetOptions(
            'f=s'    => \$filelocation,
            'd=s'    => \$datadir,
	    'h'      => \$help,
	    'help'   => \$help
          ) or usage();

if($help) 
{
  usage();
}    

# check if bgpdump exist
unless (-e $bgpdumplocation) 
{
  print "bgpdump tool does not installed in /usr/local/sbin/ directory!\n";
  exit;
} 
# check MRT file exist
unless (-e $filelocation)
{
  print "MRT file does not exist!\n";
  exit;
}
# check if data dir exist
unless (-e $datadir)
{
  print "Data directory does not exist!\n";
  exit;
}

# get filename
my @myarr = split (/\//, $filelocation);
my $update_file = $myarr[$#myarr];  #filename without directory
my $update_file_extracted = $datadir."/".$update_file.".txt"; #txt for bgpdump output


print "Extracting $update_file\n";
print("$bgpdumplocation -M $filelocation -O $update_file_extracted\n");
system("$bgpdumplocation -M $filelocation -O $update_file_extracted");

print "Analyze routing data...\n";

# peer_arr
my @tmp_arr = ();
my @peer_arr = ();

# read MRT file 
open(my $filein, $update_file_extracted) || die "couldn't open the $update_file_extracted!";
my @lines = <$filein>;
close $filein;
chomp(@lines);

# put all IP addresses in array
foreach my $item (@lines)
{
  (my $type, my $timestamp, my $mode, my $ip, my $as, my @attr_arr ) = split (/\|/, $item);
  push (@tmp_arr, $ip); 
}	

# fine unique peers IP 
my %unique = ();
foreach my $item (@tmp_arr)
{
  $unique{$item} ++;
}
@peer_arr = keys %unique;


# print peerlist  
my $peerfile;
my $ipdir; # used later in printing route data
my @tmpdatadir = split (/\//, $datadir);
if ($tmpdatadir[$#tmpdatadir] eq "/")
{
  $peerfile = $datadir."peerlist.txt";
  $ipdir = $datadir;  # dont update anything
}
else
{
  $peerfile = $datadir."/peerlist.txt";
  $ipdir = $datadir."/";  #update dir for each peer
}
open (my $OUT, ">$peerfile") || die "Cannot open $peerfile for write";
foreach my $ip (@peer_arr)
{
  print $OUT "$ip\n";
}
close $OUT;

# find final routing state for each peer
foreach my $ip (@peer_arr)
{
  my $file = $ipdir.$ip."_table.txt";
  open ( my $OUT, ">$file") || die "Cannot open $file for write";

  # get all lines that belong to peer IP
  my @arr = grep (/$ip/, @lines);
  # reverse lines
  my @revarr = reverse(@arr);
  
  my @prefix_arr = (); #array for prefixes
  my @final_arr = (); # array for final lines

  foreach my $line (@revarr)
  {
    (my $type, my $timestamp, my $mode,my $ip, my $as, my $prefix, my @attr_arr ) = split (/\|/, $line);
    if (!(grep {$_ eq $prefix} @prefix_arr)) 
    {
      push (@prefix_arr, $prefix);
      push (@final_arr, $line);
    }
  }

  foreach my $item (@final_arr)
  {
    my $with = "W";
    (my $type,my $timestamp,my $mode,my $ip, my $as, my $prefix, my @attr_arr ) = split (/\|/, $item);
    if ($mode ne $with)
    {
      print $OUT "$item\n";
    }
  }
  
  close $OUT;
}

print "Done. Files are located in $datadir\n";
