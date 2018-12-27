package BGPmon::CLI::ShowBGPRoutes;

use 5.010001;
use strict;
use warnings;
use Carp qw( croak );

require Exporter;

our $AUTOLOAD;
our @ISA = qw(Exporter);
# Items to export into callers namespace by default. Note: do not export
# names by default without a very good reason. Use EXPORT_OK instead.
# Do not simply export all your public functions/methods/constants.

# This allows declaration	use BGPmon::ShowBGPRoutes ':all';
# If you do not need this, moving things directly into @EXPORT or @EXPORT_OK
# will save memory.
our %EXPORT_TAGS = ( 'all' => [ qw( ) ] );
our @EXPORT_OK = ( @{ $EXPORT_TAGS{'all'} } );
our @EXPORT = qw( );
our $VERSION = '0.01';

my %access_fields = (
  host => 'localhost',
  port => 50000,
  handler   => undef,
  handlerParam => undef);

my %priv_fields = ();

## constructor
sub new {
  my $class = shift;
  my $self = {
   _permitted => \%access_fields,
   %access_fields,
   %priv_fields
  };
  bless ($self, $class);
  return $self;
}

## accessor functions
sub AUTOLOAD {
 my $self = shift;
 my $type = ref($self) or croak "$self is not an object";

 my $name = $AUTOLOAD;
 $name =~ s/.*://; # strip fully-qualified portion

 unless (exists $self->{_permitted}->{$name} ) {
   croak "Can't access `$name' field in class $type";
 }

 if (@_) {
   return $self->{$name} = shift;
 } else {
   return $self->{$name};
 }
}

## read the file
sub read {
  my $self = shift;

  my $data = "";
  ## log into the server
  use Net::Telnet;
  use Expect;
  my $telnet = new Net::Telnet (Host=>$self->host,Port=>$self->port)
    or die "Cannot telnet to remotehost: $!\n";
  my $t = Expect->exp_init($telnet);
  my $timeout = 10;
  my $spawn_ok;
  my ($matched_pattern_position,$error,$successfully_matching_string,$before_match,$after_match);
  $successfully_matching_string = "";
  ($matched_pattern_position,$error,$successfully_matching_string,$before_match,$after_match) 
    = $t->expect($timeout,
     [
      qr /Password:/,
      sub {
        $spawn_ok = 1;
        my $obj = shift;
        $obj->send("BGPmon\r\n");
        exp_continue;
      }
     ],
     [
      qr />/,
      sub {
        my $obj = shift;
        $obj->send("show bgp routes\r\n");
       }
      ]);
  do{
    $successfully_matching_string = "";
    ($matched_pattern_position,$error,$successfully_matching_string,$before_match,$after_match) 
      = $t->expect($timeout,
       [
         qr'Press ENTER to see more or Q to leave',
         sub {
           my $obj = shift;
           $obj->send('\r\n');
         }
       ],
       '-re', qr'>',
       [
        eof =>
        sub {
          if ($spawn_ok) {
            die "ERROR: premature EOF in login.\n";
          } else {
            die "ERROR: could not spawn telnet.\n";
          }
        }
       ],
       [
        timeout =>
        sub {
          die "No login.\n";
        }
       ]
       #'-re', qr'[#>:] $', #' wait for shell prompt, then exit expect
      );
    $data .= $before_match;
  }while($successfully_matching_string =~ /ENTER/);
  $t->send("exit\r\n");
  $t->hard_close();

  my %record;
  my @lines = split(/\n/,$data);
  foreach my $line (@lines){
    if($line =~ /([\d+\.?]+\/\d+)\s+([\d+\.?]+)\s+(\d)\s+([\d+\s?]*)/){
      $record{action}='A';
      $record{prefix}=$1;
      $record{peerIP}=$2;
      $record{pathAttrs}=$4;
      if(defined($self->{handlerParam})){
        &{$self->{handler}}($self->{handlerParam},%record);
      }else{
        &{$self->{handler}}(%record);
      }
    }
  }
  return 1;
}

sub DESTROY { }

1;
__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

BGPmon::ShowBGPRoutes - Perl extension for blah blah blah

=head1 SYNOPSIS

  use BGPmon::ShowBGPRoutes;
  blah blah blah

=head1 DESCRIPTION

Stub documentation for BGPmon::ShowBGPRoutes, created by h2xs. It looks like the
author of the extension was negligent enough to leave the stub
unedited.

Blah blah blah.

=head2 EXPORT

None by default.



=head1 SEE ALSO

Mention other useful documentation such as the documentation of
related modules or operating system documentation (such as man pages
in UNIX), or any relevant external documentation such as RFCs or
standards.

If you have a mailing list set up for your module, mention it here.

If you have a web site set up for your module, mention it here.

=head1 AUTHOR

Cathie Olschanowsky, E<lt>cathie@E<gt>

=head1 COPYRIGHT AND LICENSE

Copyright (C) 2011 by Cathie Olschanowsky

This library is free software; you can redistribute it and/or modify
it under the same terms as Perl itself, either Perl version 5.10.1 or,
at your option, any later version of Perl 5 you may have available.


=cut
