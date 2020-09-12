#!/usr/bin/perl
#
# PerlTidy Setting
# -b -l=70 -i=4 -ci=4 -lp -vt=2 -cti=0 -pt=1 -sbt=1 -nolq
# -------------------------------------------------------------------
use 5.012;    # so readdir assigns to $_ in a lone while test
use File::Copy;
use Getopt::Std;
use strict;

our %opts;
getopt( 'v:', \%opts );

# -------------------------------------------------------------------
# Static variables.
our $CurrVer = $opts{'v'} ||= '0.9.16';
our $Home = 'D:\Users\HRM.Delphinus\WoT\MODS';

# -------------------------------------------------------------------
# list mods.

chdir $Home or die;
our $dh;
our @Mods;
opendir( $dh, $Home ) or die "$!";
@Mods = grep { ( -d $_ ) and ( $_ !~ /^(\!|\.\.?)/ ) } readdir($dh);
closedir $dh;

# -------------------------------------------------------------------
# Check WoT version number of each mods, and modify if needed.

our @Target;
foreach my $mod (@Mods) {
    my $dh2;
    if ( ( -d $mod ) and ( opendir( my $dh2, $mod ) ) ) {
        my @WoTversion_of_Mod =
            grep { $_ =~ /^(\d[\d\.]+)$/ } readdir($dh2);
        my $flg_numdirs = scalar @WoTversion_of_Mod;
        if ( $flg_numdirs > 2 ) {
            print "This mod has Special structure. skipped\n";
        }
        elsif ( $flg_numdirs == 1 ) {

            # print join( ',', @WoTversion_of_Mod ), "\n";
            my $wvm = shift @WoTversion_of_Mod;
            push( @Target, [ $mod, $wvm ] ) if ( $wvm ne $CurrVer );
        }
        else {
            print "This mod has invalid version number: ",
                join( ',', @WoTversion_of_Mod ), "\n";
        }
        closedir $dh2;
    }
    else {
        print "ERR: $!";
    }
}

# print "-" x 30, "\n";
# print join( "\n", @Target ), "\n";
# print "-" x 30, "\n";

# -------------------------------------------------------------------
# Rename version number to current version of WoT

foreach my $refmod (@Target) {
    my $mod = $refmod->[0];
    my $wvm = $refmod->[1];

    # print "$mod\t$wvm => $CurrVer", "\n";
    unless ( chdir "${Home}/$mod" ) {
        print "ERR: $!";
        next;
    }

    # print "move $wvm $CurrVer\n";
    move( $wvm, $CurrVer );
    chdir $Home;
}

exit 0;

# -------------------------------------------------------------------
# Subs

sub HELP_MESSAGE() {
}

# ===================================================================
