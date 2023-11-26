#!/usr/bin/perl
#
# PerlTidy Setting
# D:\Perl64\site\bin\perltidy -b -q -bt=1 -pt=1 -lp -aws -dws -kbl=0 -dnl -l=75 $(FileNameEx)
# -------------------------------------------------------------------
# use 5.012;    # so readdir assigns to $_ in a lone while test
use File::Copy;
use File::Path qw(remove_tree);
use Getopt::Std;
use Data::Dumper;
use Term::ExtendedColor qw(:all);
use strict;
use warnings;

# Command line options.
our %opts;
getopts( 'th:l:', \%opts );

# -------------------------------------------------------------------
# Static variables.
our $home       = $opts{'h'} ||= '/var/spool/torrent';
our $mi         = '/usr/bin/env mediainfo';
our $mi_options = '--Output=Video;%Width%';
our $log        = $opts{'l'} ||= 'sulvage_mp4.log';
our $version    = '0.6.14';
our @ignoreList = ( "Series", "SingleFeatuerd", "Anime", "TEST" );
our $opening    = "Sulvage mp4 file(s) Tool Ver. $version";
our $TestSpeach = 'TEST mode enabled. DO NOT move and remove_tree()';

# Staffs
$Data::Dumper::Indent = 2;
$mi_options           = quotemeta $mi_options;

# Opening.
open( our $logfh, ">", "$home/$log" ) or die;
print $logfh "$opening\n\n";
print( fg( 'orangered1', "$TestSpeach\n" ) ) if ( $opts{'t'} );

# -------------------------------------------------------------------
# list directories
chdir $home or die "Cannot chdir() to $home : $!";
our $dh;
our @Directories;
opendir( $dh, $home ) or die "$!";
@Directories =
  grep { ( -d $_ ) and ( $_ =~ /^(?:\w+|[a-z]+?\d+|\[Thz|\[[\w\.]+)/x ) }
  readdir($dh);
closedir $dh;

# -------------------------------------------------------------------
# Check existance of MP4 file
print Data::Dumper->Dump( [ \%opts ], ["Options"] ) if ( $opts{'t'} );
DIR: foreach my $d (@Directories) {
    my $isFHD      = 0;
    my $isSplit    = 0;
    my $isFinished = 0;

    # Skip Ignore List
    next if ( grep { $d eq $_ } @ignoreList );

    # List mp4 files.
    opendir( $dh, $d ) or die "$!";
    my @files =
      grep { /[\w\-\.\[\]]+\.(mp4|wmv|mkv)$/ } readdir($dh);
    closedir $dh;
    next if ( scalar @files < 1 );    # ignore incomplete torrent.
    print $logfh '-' x 75, "\n";
    print $logfh "INFO: $d has ", scalar @files, " mp4 videos.\n";

    # Check each video files
    foreach my $f (@files) {
        my $ext       = '';
        my $fname     = '';
        my $insignia  = undef;
        my $number    = undef;
        my $subnumber = undef;

        # Prepare for pattern matching.
        study $f;

        # Parse file name section.
        if (
            $f =~ /^\[(?:Thz\.la|ThZu\.Cc|.+\.me)\]
                   \d*?
                   ([A-Za-z]+|t28|\d{2}ID)
                   \-?
                   (\d+)
                   (cd\d|CD\d)?
                   \.mp4$/x
          )
        {
            # [168x.me]1kmhr00039.mp4
            # [168x.me]36doks00435.mp4
            # [44x.me]CESD-575.mp4
            # [Thz.la]onez-130.mp4
            # [Thz.la]t28-515.mp4
            # [ThZu.Cc]rki-473.mp4
            $insignia  = $1;
            $number    = $2;
            $subnumber = ( defined $3 ) ? $3 : "none";
            if ( $subnumber ne "none" ) {
                print $logfh "\tINFO: $d has split mp4 files. Skipped\n";
                print $logfh
                  "\tINFO: $d has sub-numbered files(ex. $subnumber)\n";
                print $logfh "\tso we shouldn't do twice in this case\n";
                $isSplit = 1;
                next DIR;
            }
            else {
                print $logfh "\tDEBUG: $d has only one movie\n";
                $isFHD =
                  ( `$mi $mi_options $d/$f` == 1920 )
                  ? 1
                  : 0;
                $fname = uc($insignia) . '-' . $number;
            }
            $ext = 'mp4';
        }
        elsif (
            $f =~ /^(?:hhd800.com@)?
                   ([\d_\-]+?)\-
                   (1pon|carib|10mu|paco)
                   (?:-1080p)?
                   \.mp4$/ix
          )
        {
            # 102817_598-1pon-1080p.mp4
            # 111817-541-carib-1080p.mp4
            # 010518_01-10mu-1080p.mp4
            # 062818_295-paco-1080p.mp4
            # hhd800.com@051922_001-1PON.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = $1 . "." . lc($2);
            $ext   = 'mp4';
        }
        elsif (
            $f =~ /^(?:s?hjd2048\.com)?
                   \-?
                   (?:\d{4}|\d{2}\-\d{2})
                   ([A-Za-z]+)
                   (\d+)
                   (?:FHD|\-h?264|hhb)?
                   \.mp4$/x
          )
        {
            # 0227club452-h264.mp4
            # 0928sdmu695FHD.mp4
            # hjd2048.com-0323ssni160-h264.mp4
            # hjd2048.com-0402urlh001hhb.mp4
            # hjd2048.com0809mdtm395-h264.mp4
            # shjd2048.com-0315ssni433-h264.mp4
            # hjd2048.com-04-10vema129-h264.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = uc($1) . '-' . $2;
            $ext   = 'mp4';
        }
        elsif (
            $f =~ /^([A-Z]+)
                   \-?
                   (\d+)
                   (?:_|\-)?
                   ([\w\.]+?)?
                   \.(mp4|MP4|mkv)$/x
          )
        {
            # VENU722.mp4
            # XVSR298MP4.mp4
            # EIKI059mp4.mp4
            # MOT-248/MOT-248A.mp4
            # MOT-234/MOT-234_A.mp4
            # KTDS-793.1080p.mkv
            # ABP-554-HD.mp4
            $insignia  = $1;
            $number    = $2;
            $subnumber = ( defined $3 ) ? $3 : "none";
            $ext       = $4;
            if (    ( defined $subnumber )
                 && ( $subnumber =~ /[A-Z]/ ) )
            {
                print $logfh
                  "\tINFO: $d is split into few files. Skipped\n";
                print $logfh
                  "\tINFO: $d has sub-numbered files(ex. $subnumber)\n";
                print $logfh "\tso we should not dabble in this case \n";
                $isSplit = 1;
                next DIR;
            }
            else {
                $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
                $fname = $insignia . '-' . $number;
            }
        }
        elsif ( $f =~ /^h_\d{3,4}([a-zA-Z]+?)(\d+)\.mp4$/ ) {

            # h_1186etqr00012.mp4
            # [168x.me]h_227jukf00010/h_227jukf00010.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = uc($1) . '-' . $2;
            $ext   = 'mp4';
        }
        elsif (
            (
               $f =~ /^(?:hhd800.com@)?
                        (FC2\-PPV)\-
                        (\d+)
                        [\-\_]?
                        (\d+)?\.mp4$/x
            )
            or ( $f =~ /^(heyzo)(?:_hd)?(?:[\-_]+)(\d+)(?:_full)?\.mp4$/ )
          )
        {
            # FC2-PPV-809942_1.mp4
            # hhd800.com@FC2-PPV-3069918.mp4
            # heyzo_hd_1613_full.mp4
            $insignia  = $1;
            $number    = $2;
            $subnumber = ( defined $3 ) ? $3 : "none";
            if ( $subnumber ne 'none' ) {

                # Sepalated movies.
                print $logfh
                  "\tINFO: $d is split into few files. Skipped\n";
                print $logfh
                  "\tINFO: $d has sub -numbered files(ex. $subnumber)\n";
                print $logfh " \tso we should not dabble in this case.\n";
                $isSplit = 1;
                next DIR;
            }
            elsif ( $subnumber eq 'none' ) {

                # This movie is one file. Not separated.
                $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
                $fname = $insignia . '-' . $number;
                $ext   = 'mp4';
            }
            else {
                my $emerge = fg( 'red1', "Unknow format of filename: $f" );
                print STDERR bold("$emerge\n");
                exit 201;
            }
        }
        elsif (
            $f =~ /^\d*
                   ([a-z]+?|t28)
                   \-?
                   ([\d]+?)
                   (?:_hd|FHD|\-h264|z)?
                   \.mp4$/x
          )
        {
            # abp660_hd.mp4
            # xrw457.mp4
            # vec305-h264.mp4
            # t28-541.mp4
            # [168x.me]emrd00090/emrd00090.mp4
            # [168x.me]49ekdv00533/49ekdv00533.mp4
            # [168x.me]mmkz-044/mmkz-044.mp4
            # [7sht.me]ibw-690z/ibw-690z.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = uc($1) . '-' . $2;
            $ext   = 'mp4';
        }
        elsif (
            $f =~ /^(?:freedl|chd1080|hhd800)\.(?:com|org)\@
                   (?:nomask60fps_|\d{3})?
                   ([a-zA-Z]+?|\d{2}ID)
                   \-?
                   (\d{3,5})
                   [A-Z]?
                   (?:hhb_1080P|_uncensored)?
                   \.(mp4|mkv)/x
          )
        {
            # chd1080.com@nomask60fps_hnd00292hhb_1080P.mp4
            # hhd800.com@BF-631.mp4
            # hhd800.com@420POW-001.mp4
            # hhd800.com@KTRA-289E.mp4
            # 29ID-024/hhd800.com@29ID-024.mp4
            # freedl.org@BBAN-381.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = uc($1) . '-' . sprintf( "%03d", "$2" );
            $ext   = $3;
        }
        elsif (
            $f =~ /^(?:gg5.co@)
                   ([A-Za-z]+?)-(\d{2,3})
                   (?:-C_GG5)
                   \.(mp4|mkv)/x
          )
        {
            # gg5.co@MDON-036-C_GG5.mp4
            $isFHD = ( `$mi $mi_options $d/$f` == 1920 ) ? 1 : 0;
            $fname = uc($1) . '-' . sprintf( "%03d", "$2" );
            $ext   = $3;
        }
        else {
            # Invalid useless videos.
            print $logfh "\tNOTICE: INVALID: $d/$f\n";
            next;
        }

        # Filename manipulation
        $fname .= ".1080p" if ($isFHD);
        $fname .= ( $ext ne '' ) ? ".$ext" : '.mp4';
        print $logfh "\tINFO: DIST: $fname\n";

        # Move file -------------------------------------------------
        if ( -e "$home/$fname" ) {
            my $log =
              bold("WARN: ")
              . "$fname is already exist in $home. Ignored\n";
            $log = fg( 'yellow1', $log );
            print STDERR $log;
            $isFinished = 0;
            next;
        }
        else {
            if ( $opts{'t'} ) {
                print $logfh "\tDEBUG: move $d/$f $home/$fname\n";
            }
            else {
                move( "$d/$f", "$home/$fname" );
            }
            $isFinished = 1;
        }
    }    # File loop end.

    # ---------------------------------------------------------------
    # Remove directory
    if ( !$isFinished ) {
        print $logfh "\tWARN: $d is NOT finished by some reason.\n";
        next DIR;
    }
    if ( $opts{'t'} ) {
        print $logfh "\tNOTICE: remove_tree($d)\n";
        next DIR;
    }
    else {
        no strict 'refs';
        remove_tree( $d, { 'error' => \my $refErr } );
        if ( ( defined $refErr ) and ( scalar @{$refErr} ) ) {
            for my $diag ( @{$refErr} ) {
                my ( $file, $message ) = %{$diag};
                if ( $file eq '' ) {
                    print $logfh "ERR: general error $message \n";
                }
                else {
                    print $logfh
                      "ERR: problem unlinking $file : $message \n";
                }
            }
        }
        else {
            print $logfh "\tDEBUG: No error encountered on $d\n";
        }
        use strict 'refs';
    }
}    # Directory loop end.
close($logfh);
exit 0;

# -------------------------------------------------------------------
# Subs
sub HELP_MESSAGE() {
}

# ===================================================================
