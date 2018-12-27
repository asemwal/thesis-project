package BGPmon::MRT::BgpdumpReader;

use 5.010001;
use strict;
use warnings;
use Carp qw( croak );
use File::ReadBackwards ;

require Exporter;

our $AUTOLOAD;
our @ISA = qw(Exporter);
# Items to export into callers namespace by default. Note: do not export
# names by default without a very good reason. Use EXPORT_OK instead.
# Do not simply export all your public functions/methods/constants.

# This allows declaration	use BGPmon::BgpdumpReader ':all';
# If you do not need this, moving things directly into @EXPORT or @EXPORT_OK
# will save memory.
our %EXPORT_TAGS = ( 'all' => [ qw( ) ] );
our @EXPORT_OK = ( @{ $EXPORT_TAGS{'all'} } );
our @EXPORT = qw( );
our $VERSION = '0.01';

my %access_fields = (
  bgpdataEXE=> undef,
  inputFile => undef,
  readReverse => 0,
  handlerParam => undef,
  handler   => undef);

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
  if($self->{readReverse}){
    if(!tie *FILE, 'File::ReadBackwards', $self->{inputFile}){
      return 0;
    }
  }else{
    if(!open(FILE,$self->{inputFile})){
      print STDERR "Failure: $!\n";
      return 0;
    }
  }
  my @data;
  my %record;
  while(<FILE>){
    my $line = $_;
    @data = split /\|/, $line;  
    $record{timestamp}=$data[1];
    $record{action}=$data[2];
    $record{peerIP}=$data[3];
    $record{peerAS}=$data[4];
    $record{prefix}=$data[5];
    $record{pathAttrs}=$data[6];
    $record{type}=$data[7];
    if(defined($self->{handlerParam})){
      &{$self->{handler}}($self->{handlerParam},%record);
    }else{
      &{$self->{handler}}(%record);
    }
  }
  close(FILE);
  return 1;
}

sub DESTROY { }

1;
__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

BGPmon::BgpdumpReader - Perl extension for blah blah blah

=head1 SYNOPSIS

  use BGPmon::BgpdumpReader;
  blah blah blah

=head1 DESCRIPTION

Stub documentation for BGPmon::BgpdumpReader, created by h2xs. It looks like the
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
