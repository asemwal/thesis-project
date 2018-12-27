package BGPmon::RoutingTable;

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

# This allows declaration	use BGPmon::RoutingTable ':all';
# If you do not need this, moving things directly into @EXPORT or @EXPORT_OK
# will save memory.
our %EXPORT_TAGS = ( 'all' => [ qw( ) ] );
our @EXPORT_OK = ( @{ $EXPORT_TAGS{'all'} } );
our @EXPORT = qw( );
our $VERSION = '0.01';

my %access_fields = (
  table   => {});

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

sub getAttr{
  my $self = shift;
  my %prefix = @_;
  return $self->{table}->{$prefix{peerIP}}->{$prefix{prefix}}->{attrs};
}
sub getAction{
  my $self = shift;
  my %prefix = @_;
  return $self->{table}->{$prefix{peerIP}}->{$prefix{prefix}}->{action};
}

sub prefixExists{
  my $self = shift;
  my %prefix = @_;
  if(defined($self->{table}->{$prefix{peerIP}}->{$prefix{prefix}}->{attrs})){
    return 1;
  }
  return 0;
}

## addPrefix
sub addPrefix{

  my $self = shift;
  my %prefix = @_;
 
  $self->{table}->{$prefix{peerIP}}->{$prefix{prefix}}->{attrs}=$prefix{pathAttrs}; 
  $self->{table}->{$prefix{peerIP}}->{$prefix{prefix}}->{action}=$prefix{action}; 

}

sub peerExists{
  my $self = shift;
  my $peerIP = shift;
  return defined($self->{table}->{$peerIP});
}

sub addPrefixIfNew{
  my $self = shift;
  my %prefix = @_;
  if(!$self->prefixExists(%prefix)){
    $self->addPrefix(%prefix);
  }
  return 1;
}

sub  equivalentTo{
  my $self = shift;
  my $otherTable = shift;

  if($self->containedBy($otherTable) && $otherTable->containedBy($self)){
    return 1;
  }
  return 0;

}

sub containedBy{
  my $self = shift;
  my $otherTable = shift;
  my %prefix;
  my $error = 0;

  foreach my $peer (keys %{$self->{table}}){
    if(!$otherTable->peerExists($peer)){
      $error +=1;
      print STDERR "Peer $peer does not exist in one of the tables\n";
    }else{
      foreach my $prefix (keys %{$self->{table}->{$peer}}){
        $prefix{peerIP} = $peer;
        $prefix{prefix} = $prefix;      
        if($self->{table}->{$peer}->{$prefix}->{action} eq 'A'){
          if(!$otherTable->prefixExists(%prefix)){
            print STDERR "peerIP: $peer prefix: $prefix does not exist in one of the tables\n";
            $error+=1;
          }else{
            my $attrs = $otherTable->getAttr(%prefix);
            my $action = $otherTable->getAction(%prefix);
            if($action ne $self->{table}->{$peer}->{$prefix}->{action}){
              print STDERR "peerIP: $peer prefix: $prefix action does not match\n";
              $error+=1;
            }
            if($attrs ne $self->{table}->{$peer}->{$prefix}->{attrs}){
              print STDERR "peerIP: $peer prefix: $prefix attrs do not match\n";
              $error+=1;
            }
          }
        }
      }
    }
  }
  if($error){
    print STDERR "$error errors occurred\n";
    return 0;
  }
  return 1;
}

sub DESTROY { }

1;
__END__
# Below is stub documentation for your module. You'd better edit it!

=head1 NAME

BGPmon::RoutingTable - Perl extension for blah blah blah

=head1 SYNOPSIS

  use BGPmon::RoutingTable;
  blah blah blah

=head1 DESCRIPTION

Stub documentation for BGPmon::RoutingTable, created by h2xs. It looks like the
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
