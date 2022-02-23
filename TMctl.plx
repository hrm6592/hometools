#!/usr/bin/perl
# -b -q -bt=1 -pt=1 -lp -aws -dws -kbl=0 -dnl -l=75
# ------------------------------------------------------------------------
use Data::Dumper;
use Getopt::Std;
use JSON::XS;
use LWP::UserAgent;
use Term::ExtendedColor qw(:all);
use strict;

# Command line options.
our %opts;
getopts( 'am:d:r:lf', \%opts );

# Subs
sub getList (;$);
sub getFinishiedList ($;$);
sub removeTorrent ($);

# Objects preparation
our $json = JSON::XS->new->ascii->pretty;
our $ua   = LWP::UserAgent->new( agent => 'Transmission-Client' );

# ------------------------------------------------------------------------
# Default settings.
our $uri = 'http://192.168.1.102:9091/transmission/rpc';
$Data::Dumper::Indent = 2;
our $minSeeders     = $opts{'m'} ||= 5;
our $dateLimit      = ( $opts{'d'} ||= 150 ) * 86400;    # seconds.
our $seedRatioLimit = $opts{'r'} ||= undef;
our $dataLimitMode  = $opts{'a'} ? 'addedDate' : 'dateCreated';

# ------------------------------------------------------------------------
# Remove mode if needed.
print bold("Transmission API controller.\n");
if ($seedRatioLimit) {
    die("Specify seeding limit ratio in number!\n")
      unless ( $seedRatioLimit =~ /^[0-9\.]+$/ );
    print "Settings: MAX Seeding Ratio : ${seedRatioLimit}\n";
    my $refFinishedList = getFinishiedList($seedRatioLimit);
    if ( $opts{'l'} ) {

        # List mode.
        print Data::Dumper->Dump( [$refFinishedList], [qw(CompletedIds)] );
        exit 0;
    }
    print fg( 'red2', [ "\n", 'Remove seeding completed torrents.', "\n" ] );
    removeTorrent($refFinishedList);
    exit 0;
}
else {
    print "Settings: Minimum seeder per torrent : ${minSeeders}\n";
    print "Settings: Date Limit Mode            : ",
      bold( ${dataLimitMode} ), "\n";
    print "Settings: Maximum Date limit         : ", ${dateLimit} / 86400,
      " days.\n";
}

# ------------------------------------------------------------------------
# Get Torrent list
our $sid = "";
our $jTrList;
getList();

# List which torrent we have to download now
# print Data::Dumper->Dump( [ $json->decode($jTrList) ],
#                           [qw (JSONtorrentList)] );
our @needDownload;
our %TrNameList;
foreach my $t ( @{ $json->decode($jTrList)->{"arguments"}->{"torrents"} } ) {
    my $sCount = 0;
    foreach my $s ( @{ $t->{'trackerStats'} } ) {
        $sCount += ( $s->{'seederCount'} < 0 ) ? 0 : $s->{'seederCount'};
    }
    if (   ( $sCount < $minSeeders )
        or ( time - $t->{$dataLimitMode} > $dateLimit ) )
    {
        push @needDownload, $t->{"id"};
        $TrNameList{ $t->{"name"} } = $sCount;
    }
}

# ------------------------------------------------------------------------
# Start download listed torrents.
our $reqTrStart = {
    'method'    => 'torrent-start',
    'arguments' => { 'ids' => \@needDownload },
};
if ( $opts{'l'} ) {
    print Data::Dumper->Dump( [ \%TrNameList ], [qw(TorrentName)] );
    exit 0;
}
our $res = $ua->post( $uri, 'Content' => $json->encode($reqTrStart) );
print Data::Dumper->Dump( [ $json->decode( $res->content ) ], [qw(Result)] );

# ------------------------------------------------------------------------
# Subs
sub getList (;$) {
    my $nested    = shift;
    my $reqTrList = {
        'method'    => 'torrent-get',
        'arguments' => {
            'fields' =>
              [ 'id', 'name', 'addedDate', 'dateCreated', 'trackerStats' ],
        },
        tag => int rand 2 * 32 - 1,
    };
    $ua->default_header( 'X-Transmission-Session-Id' => $sid );

    # Get torrent informations.
    my $res = $ua->post( $uri, 'Content' => $json->encode($reqTrList) );

    # Check it out.
    unless ( $res->is_success ) {
        if ( ( $res->code == 409 ) and ( !$nested ) ) {
            $sid = $res->header('X-Transmission-Session-Id');
            getList(1);
        }
        else {
            print "Error: ", $res->code, "\n";
            return undef;
        }
    }
    else {
        # request succeeded.
        # print Dumper( $res->headers );
        # print "Response Data structure is ", ref $res->content, "\n";
        # print $json->decode( $res->content ), "\n";
        # print Data::Dumper->Dump( [ $res->content ], [qw(ResponseData)] );
        $jTrList = $res->content;
        return 1;
    }
    return undef;
}

sub getFinishiedList ($;$) {
    my $limit     = shift;
    my $nested    = shift;
    my @completed = ();
    my $reqTrList = {
        'method'    => 'torrent-get',
        'arguments' => {
            'fields' => [ 'id', 'name', 'uploadRatio', 'isFinished' ],
        },
        tag => int rand 2 * 32 - 1,
    };
    $ua->default_header( 'X-Transmission-Session-Id' => $sid );

    # Get torrent informations.
    my $res = $ua->post( $uri, 'Content' => $json->encode($reqTrList) );

    # Check it out.
    unless ( $res->is_success ) {
        if ( ( $res->code == 409 ) and ( !$nested ) ) {
            $sid = $res->header('X-Transmission-Session-Id');
            getFinishiedList( $limit, 1 );
        }
        else {
            print "Error: ", $res->code, "\n";
            return undef;
        }
    }
    else {
        # request succeeded.
        foreach my $t (
            @{ $json->decode( $res->content )->{"arguments"}->{"torrents"} } )
        {
            next if ( ${ $t->{'isFinished'} } != 1 );
            next if ( $t->{'uploadRatio'} < $limit );
            push @completed, $t->{'id'};
        }
        return \@completed;
    }
}

sub removeTorrent ($) {
    my $refList     = shift;
    my $reqTrRemove = {
        'method'    => 'torrent-remove',
        'arguments' => { 'ids' => $refList },
    };

    # print Data::Dumper->Dump( [$reqTrRemove], [qw(RemoveList)] );
    my $res = $ua->post( $uri, 'Content' => $json->encode($reqTrRemove) );
    print Data::Dumper->Dump( [ $json->decode( $res->content ) ],
        [qw(Result)] );
    return 0;
}

# ========================================================================
