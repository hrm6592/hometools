#!/usr/bin/perl
# find encoded file from specififed WMV files and display
# some informations.
#
# PerlTidy Setting
# -b -l=70 -i=4 -ci=4 -lp -vt=2 -cti=0 -pt=1 -sbt=1 -nolq
# ----------------------------------------------------------
# Module loading.
use File::Basename;
use File::Find;
use Getopt::Std;

# Command line options.
our %opts = ();
getopts( 'es:h:', \%opts );

# Fixed variables and etc.
our $home   = $opts{'h'} ||= '/var/spool/enctemp';
our $Stored = $opts{'s'} ||= '/var/spool/torrent/TEST';
our $regTgtFiles = qr/^[0-9A-Za-z][\w\-]+\.(avi|mp4|wmv|mkv)$/;
our $regFileType = qr/\.(avi|mp4|wmv|mkv)$/;

# List WMV files.
opendir( my $dh, $home ) or die;
our @WMVs =
  grep { ( -f "$home/$_" ) and ( $_ =~ /$regFileType$/ ) } readdir($dh);
closedir $dh;

# List Temporary files
opendir( my $dh, $Stored ) or die;
our @Stored = grep { -f "$Stored/$_" } readdir($dh);
closedir $dh;
chdir $home or die;
our @refAVIs = ();
foreach my $f (@WMVs) {

    # exclusions
    next
      if (    ( !-f $f )
           or ( $f =~ /\.\.?$/ )
           or ( $f !~ /$regTgtFiles/ ) );

    # check it be encoded or not.
    my $wmv      = $f;
    my $basename = fileparse( "${home}/$f", qr/$regFileType$/ );
    my @dest     = grep { /$basename/ } @Stored;
    push @refAVIs,
      (
          ( scalar @dest )
        ? [ $wmv, \@dest ]
        : [ $wmv, undef ]
      );
}

# ----------------------------------------------------------
# Display infomations
print "HOME         : $home\n";
print "STORED       : $Stored\n";
print "Target files : ", scalar @WMVs, "\n";
print "--" x 15, "\n";
if ( defined $opts{'e'} ) {

    # shell script helper mode.
    foreach my $refA (@refAVIs) {
        next if ( !defined $refA->[1] );
        my $w = $refA->[0];
        my $a = $refA->[1]->[0];
        print "mv $Stored/$a \\\n   \'\' ;\\\n";
        print "rm $home/$w ;\\\n";
    }
}
else {
    foreach my $refA (@refAVIs) {
        my $w = $refA->[0];
        print "$w\t", join( ', ', @{ $refA->[1] } ), "\n";
    }
}
exit 1;

# ----------------------------------------------------------
# Subs
sub HELP_MESSAGE() {
    print <<_EOL_;
  -e hoge
  -s
  -h
_EOL_
}

# ==========================================================
