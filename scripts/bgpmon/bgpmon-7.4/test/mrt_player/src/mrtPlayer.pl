#!/usr/bin/perl
#* 
# *
# *      Copyright (c) 2012 Colorado State University
# * 
# *      Permission is hereby granted, free of charge, to any person
# *      obtaining a copy of this software and associated documentation
# *      files (the "Software"), to deal in the Software without
# *      restriction, including without limitation the rights to use,
# *      copy, modify, merge, publish, distribute, sublicense, and/or
# *      sell copies of the Software, and to permit persons to whom
# *      the Software is furnished to do so, subject to the following
# *      conditions:
# *
# *      The above copyright notice and this permission notice shall be
# *      included in all copies or substantial portions of the Software.
# *
# *      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# *      EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# *      OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# *      NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# *      HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# *      WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# *      FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# *      OTHER DEALINGS IN THE SOFTWARE.\
# * 
# * 
# *  File: mrtPlayer.pl
# *      Authors: Dan Massey, Cathie Olschanowsky
# *  Date: Mar 12, 2012
# */

use strict;
use Getopt::Long;
use POSIX qw/strftime/;
use IO::Socket;

$| = 1;

# some erorr handling and debugging variables
my $debug = 0;
my $bytesread = 0;
my $msgsread = 0;
my $filename = "no file set";
my $verbose = 0;
# verbose can be set from the command line options

#-----   main program -----

# set from command line options
my ($list_url, $server, $port) = parseCommandLine();

# connect to BGPmon that will receive the MRT data
my $bgpmon = connectBGPmon($server, $port);

# fetch the list of files
logMsg("Archiving MRT data from $list_url");
my @file_index = fetchFileList($list_url);

## foreach line in the file check to see if it represents an update file
## if so, fetch the file, process it and remove it
my $filename; 
foreach my $line (@file_index){
  ## get the filenames
  if($line =~ /a href="(.*?bz2)"/){
    $filename = fetchFile($1, $list_url);
    validateAndSend($bgpmon, $filename);
    cleanUp($filename);
  }
}
logMsg("Finished proccesing  MRT data from $list_url");
exit 0;

#-----   parse command line  and set default values -----
sub parseCommandLine {
  debugMsg("starting parseCommandLine");

  # init Default Settings
  my $collector = "route-views.sydney";
  my $year = "2012";
  my $month = "01";
  my $list_url = "http://archive.routeviews.org/COLLECTOR/bgpdata/YEAR.MONTH/UPDATES/";
  my $server = "127.0.0.1";
  my $port = 49999;


  # Parse the command line options
  my $result = GetOptions( "collector=s" => \$collector,
			 "year=s" => \$year, 
			 "month=s" => \$month, 
                         "v" => \$verbose,
			 "port=i" => \$port, 
                         "server=s" => \$server);
  die "Usage: MRT_feeder [-v] [-collector name] [-year YYYY] [-month MM] [-server A.B.C.D] [-p port] \n" unless $result;

  #DM:   we should sanity check the input here,   collector is from the list below,  
  # year is 4 digit number between 1990 and 2090,  
  #      month is a two digit value betwen 00 and 12,   peer is a valid v4 or v6 address
  #List of collectors, "route-views.eqix",
  #"route-views.isc","route-views.kixp","route-views.linx",
  #"route-views.saopaulo","route-views.sydney","route-views.wide","route-views4",
  #"route-views6"
 
  # Set the URL to find MRT data
  $list_url =~ s/COLLECTOR/$collector/;
  $list_url =~ s/YEAR/$year/;
  $list_url =~ s/MONTH/$month/;
  debugMsg("URL is $list_url");
  debugMsg("Server is at $server, port $port");

  debugMsg("ending parseCommandLine");
  return $list_url, $server, $port;
}

#----- print a debug message -----
sub debugMsg {
  my $msg = shift;
  if ($debug) {
    print "DEBUG:  $msg \n";
  }
}

#----- log a message -----
sub logMsg {
  my $msg = shift;
  if ($verbose == 1) {
    print strftime('%D %T - ',localtime);
    print "$msg \n";
  }
}

#----- log a warning -----
sub logWarn {
  my $msg = shift;
  print STDERR strftime('%D %T - ',localtime);
  print STDERR "ERROR - $msg \n";
}

#----- log a fatal message and exit -----
sub logFatal {
  my $msg = shift;
  print STDERR strftime('%D %T - ',localtime);
  print STDERR "ERROR - $msg \n";
  exit 1;
}

#----- log a fatal message during file reading and exit -----
sub logFatalRead {
  my $msg = shift;
  print STDERR strftime('%D %T - ',localtime);
  print STDERR "ERROR - $msg (in $filename)\n";
  if ($verbose == 1) {
    print STDERR "        in message $msgsread around byte $bytesread\n";
  }
  close(FILE);
  exit 1;
}

#----- connect to BGPmon and return socket for writing data -----
sub connectBGPmon {
  debugMsg("starting connectBGPmon");
  my($server, $port) = @_;
  # connect to the BGPmon instance listening for MRT data
  logMsg("Connecting to BGPmon listening at $server port $port");
  my $sock = new IO::Socket::INET (PeerAddr => $server, PeerPort => $port, Proto => 'tcp', )
    or logFatal("Couldn't connect to $server on port $port : $!");
  debugMsg("ending connectBGPmon");
  return $sock;
} 

#----- fetch the list of update files -----
sub fetchFileList {
  debugMsg("starting fetchFileList");
  my $list_url = shift;

  ## fetch the index file to get a list of update files available
  my @html_index = `curl -# $list_url`;
  if($?){
    logFatal("Problem fetching the index file from $list_url: %!");
  }
  debugMsg("ending fetchFileList");
  return (@html_index);
}

#----- fetch an MRT update file and uncompress it -----
sub fetchFile {
  my ($file, $url)  = @_;
  debugMsg("starting fetchFile");
  debugMsg("file is $file,  url is $url");

  my $file_url = $url.$file;
  logMsg("Fetching update file $file_url");

  debugMsg("trying curl -# $file_url -o $file");
  # if file we are about to download already exists, remove it
  if (-e $file)
  { 
    logWarn("$file already exists.  removing existing file");
    cleanUp($file);
  }
  `curl -# $file_url -o $file`;
  if($?){
    logFatal("Problem fetching the update file $url");
  }

  my $compressedfile = $file;
  $file =~ s/\.bz2//;
  debugMsg("trying bunzip2 $compressedfile");
  logMsg("Unzipping file $compressedfile");
  if (-e $file)
  { 
    logWarn("$file already exists.  removing existing file");
    cleanUp($file);
  }
  `bunzip2 $compressedfile`;
  if($?){
    logFatal("Problem with unzip $compressedfile");
    exit;
  }
  debugMsg("uncompressed filename is $file");

  debugMsg("ending fetchFile");
  return $file;
}

#----- validate and send the data in the file -----
sub validateAndSend {
  my ($bgpmon, $filename) = @_;
  debugMsg("starting validateAndSend");

  logMsg("Validating and sending file $filename");

  # open the binary file for reading
  open(FILE, $filename)
    or logFatal("Couldn't open $filename for reading $!");
  binmode FILE;

  # reset our counters for logging and error reporting
  $msgsread = 1;  
  $bytesread = 0;

  debugMsg("opened and starting to read $filename");
  # read, validate, and send the data one MRT message at a time
  while( readAndSendMRT($bgpmon) ) {
    $msgsread++;
  }
  debugMsg("finished reading $filename");
  debugMsg("read $msgsread messages and $bytesread bytes");

  # close file and return
  close(FILE);
  logMsg("Sent $msgsread messages ($bytesread bytes) from file $filename");

  debugMsg("ending validateAndSend");
  return;
}

#----- read, validate, and send an MRT message -----
# returns 1 if message sent,  0 if end of File reached
sub readAndSendMRT {
  my $bgpmon = shift;
  debugMsg("starting readAndSendMRT");

  my($hdrlen, $time, $type, $subtype, $length, $hdrbytes) = readMRTHeader();
  # if length is 0,  we reached the end of the file
  if ($length == 0) { 
    return 0;
  }
  $bytesread += $hdrlen;
  debugMsg("returned $hdrlen header bytes; time=$time, type=$type, subtype=$subtype, length=$length");

  my $databytes = readAndValidateMRTData($time, $type, $subtype, $length);  
  $bytesread += $length;
  debugMsg("read $length data bytes");

  # combine the hdr and data
  my $sendlength = $hdrlen + $length;
  my $sendbytes = $hdrbytes.$databytes;

  # send the result to BGPmon
  debugMsg("writing $sendlength bytes to socket");
  my $len = syswrite($bgpmon, $sendbytes, $sendlength);
  # check for valid syswrite
  if (!defined($len) )  {
    LogFatal("problem writing to BGPmon connection");
  }
  if ($len != $sendlength) {  
    logFatal("expected to write $sendlength bytes, but only wrote $len bytes");
  }
  debugMsg("send to socket succeeded");

  debugMsg("ending readAndSendMRT");
  return $sendlength;
}

#----- cleanup the file once we are done -----
sub cleanUp {
  my $filename = shift;
  debugMsg("starting cleanUp");
  logMsg("Removing file $filename");
  debugMsg("trying rm -f $filename");
  `rm -f $filename`; 
  if($?){
    logFatal("problem removing file $filename: %!");
  }
  debugMsg("ending cleanUp");
}

#===== read an MRT Header =====
sub readMRTHeader {
  debugMsg("starting readMRTHeader");

  my $mrthdr;
  # Expect an MRT header to be a: 
  # 4 byte timestamp,  2 byte type,  2 byte subtype, 4 byte length 
  my $mrthdrsize = 12;

  # read the MRT header from the file
  my $len = sysread(FILE, $mrthdr, $mrthdrsize);

  # check for valid sysread
  if (!defined($len) )  {
      logFatalRead("problem reading MRT header from file");
  }

  # if nothing more to read, we reached the end of the file
  if ($len == 0) {  
      return ($mrthdrsize, 0, 0, 0, 0, 0); 
  }

  # if we read something,  make sure it is a complete MRT header
  if ($len != $mrthdrsize) {  
    logFatalRead("reading $mrthdrsize byte MRT header, but only found $len bytes");
  }

  #get the fields from the MRT header 
  my ($time, $type, $subtype, $length) = unpack( "N n n N", $mrthdr );
  debugMsg("read time=$time, type=$type, subtype=$subtype, length=$length");

  debugMsg("ending readMRTHeader");
  return ($mrthdrsize, $time, $type, $subtype, $length, $mrthdr);
}

#===== read and Validate an MRT Message =====
sub readAndValidateMRTData {
  debugMsg("starting readAndValidateMRTData");
  my ($time, $type, $subtype, $length) = @_;  

  # read the MRT data from the file
  my $mrtdata;
  my $len = sysread(FILE, $mrtdata, $length);

  # check for valid sysread
  if (!defined($len) )  {
      logFatalRead("problem reading MRT data from file");
  }

  # if we read something,  make sure it is a complete MRT message
  if ($len != $length) {  
    logFatalRead("reading $length byte MRT data, but only found $len bytes");
  }
  debugMsg("read $length data bytes,  now validating data");

  # now validate the MRT message 
  # we currently support only type = BGPMP4 = 16
  if ($type == 16) {
    if ( ($subtype == 0) || ($subtype == 5) ) {
      #  BGP4MP_STATE_CHANGE or BGP4MP_STATE_CHANGE_AS4
      validateStateChange($mrtdata, $subtype, $length);
    } elsif ( ($subtype == 1) || ($subtype == 4) ) {
      # BGP4MP_MESSAGE or BGP4MP_MESSAGE_AS4
      validateMRTBGP($mrtdata, $subtype, $length);
    } else {
      logFatalRead("invalid MRT (type,subtype) of ($type,$subtype)");
    }
  } else {
    logFatalRead("invalid MRT type of $type");
  }
  debugMsg("$length data bytes appear valid");

  debugMsg("ending readAndValidateMRTData");
  return $mrtdata;
}

#===== Validate an MRT State Change =====
# type = 16 subtype = 0; BGP4MP_STATE_CHANGE 
# type = 16 subtype = 5; BGP4MP_STATE_CHANGE_AS4 
sub validateStateChange {
  my ($data, $subtype, $mrtlength) = @_;
  debugMsg("starting validateStateChange");

  # this function validates type 16,  subtype 0 or 5
  if (($subtype != 5) && ($subtype != 5) )  {  
    logFatal("validateStateChange called with a subtype of $subtype");
  }

  # for 2 byte ASNs, a state change is 20 bytes for v4 peers and 44 for v6 peers
  if (($subtype == 0) && ($mrtlength != 20) & ($mrtlength != 44))  {  
    logFatalRead("invalid MRT State Change (subtype = $subtype) size of $mrtlength");
  }

  # for 4 byte ASNs, a state change is 24 bytes for v4 peers and 48 for v6 peers
  if (($subtype == 5) && ($mrtlength != 24) & ($mrtlength != 48))  {  
    logFatalRead("invalid MRT State Change (subtype = $subtype) size of $mrtlength");
  }

  debugMsg("ending validateStateChange");
  return;
}


#===== Parse and Validate an MRT BGP Message =====
# type = 16 subtype = 1; BGP4MP_MESSAGE 
# type = 16 subtype = 4; BGP4MP_MESSAGE_AS4 
sub validateMRTBGP {
  my ($data, $subtype, $mrtlength) = @_;
  debugMsg("starting validateMRTBGP");

  # this function validates type 16,  subtype 1 or 4
  if (($subtype != 1) && ($subtype != 4) )  {  
    logFatal("validateMRTBGP called with a subtype of $subtype");
  }

  my $subHdrLen = validateMRTBGPsubHdr($data, $subtype, $mrtlength);

  validateBGPMsg($data, $subHdrLen, $mrtlength);

  debugMsg("ending validateMRTBGP");
  return;
}

sub validateMRTBGPsubHdr {
  my ($data, $subtype, $mrtlength) = @_;
  debugMsg("starting validateMRTBGPsubHdr");

  # the subhdr length varies 
  # - it depends on whether AS numbers are 2 or 4 bytes
  #   this is determined by the subtype
  # - it depends on whether IP addresses are v4 or v4 
  #   this is determined by the AFI in the subhdr

  # the initial part of MRT subtype header contains 
  # peer AS (2 or 4 bytes),  local AS (2 or 4 bytes),  
  # interface (2 bytes), and AFI (2 bytes)
  debugMsg("parse first part of the MRT sub header");
  my $subhdrlen;
  my $format;
  if ($subtype == 1) {
    # 2 byte ASNs
    $subhdrlen = 8;
    $format = "n n n n"; 
  } else {
    # 4 byte ASNs
    $format = "N N n n";
    $subhdrlen = 12;
  }
  if ($subhdrlen > $mrtlength) {
    logFatalRead("MRT sub-header (subtype = $subtype) requires $subhdrlen bytes, but MRT length is only $mrtlength");
  }
  my ($peeras, $localas, $interface, $afi, $data1) = unpack( $format, $data );
  debugMsg("parsed Peer AS = $peeras,  Local AS = $localas,  Interface = $interface,  AFI = $afi");


  # now we have the AFI,  calculate the size for the  of the subHdr is just two IP addresses
  debugMsg("parsing the rest of the MRT sub header");
  if ($afi == 1) { 
    # two 4 byte IP addresses
    $subhdrlen += 8;
  } elsif ($afi == 2) { 
    # two 16 byte IP addresses
    $subhdrlen += 32;
  } else {
    logFatalRead("invalid MRT BGP Message AFI of $afi");
  }
  if ($subhdrlen > $mrtlength) {
    logFatalRead("MRT sub-header (subtype = $subtype) requires $subhdrlen bytes, but MRT length is only $mrtlength");
  }

  debugMsg("calculated MRT sub header is $subhdrlen bytes long");


  debugMsg("ending validateMRTBGPsubHdr");
  return $subhdrlen;
}

sub validateBGPMsg {
  my ($data, $subhdrlen, $mrtlength) = @_;
  debugMsg("starting validateBGPMsg");

  # the data should consist of 
  # - a $subhdrlen MRT sub-header
  # - a 16 byte BGP marker that is expected to have all bits set to 1
  # - a 2 byte BGP length
  # - a 1 byte BGP type
  my @results = unpack("C$subhdrlen C16 n C", $data);

  # in the resutls array, the BGP length follows $subhdrlen bytes of data + 16 bytes of marker 
  my $bgplen = $results[$subhdrlen + 16];

  # in the resutls array, the BGP type follows the BGP length (which is one element in results)
  my $bgptype =  $results[$subhdrlen + 17]; 

  debugMsg("parsed BGP length is $bgplen and BGP type is $bgptype,  checking marker bytes");

  # check all the BGP marker bytes have all bits set to 1 (= 255 as unsigned number)
  for(my $i=0; $i < 16; $i++) { 
    if ($results[$i+$subhdrlen] != 255) {
      logFatalRead("MRT BGP Message BGP marker byte $i does not have all bits set to 1");
    }
  }

  # check the reported MRT length really makes the subheader + BGP message length
  my $totallen = $subhdrlen + $bgplen; 
  debugMsg("calculated total length should be $totallen");
  if ($totallen != $mrtlength) {
    logFatalRead("MRT BGP Message should requires $totallen bytes, but MRT length is $mrtlength");
  }

  debugMsg("ending validateBGPMsg");
  return;
}
