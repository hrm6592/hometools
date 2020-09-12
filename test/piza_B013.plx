#!/usr/bin/perl
#
use Data::Dumper;
$Data::Dumper::Indent = 2;
our $a, $b, $c, $numtrains, $startTime;
our $timeLimit = 8 * 60 + 59;
our @lines, @trscd;
@lines = @trscd = ();
while ( ( my $input = <DATA> ) !~ /^$/ ) {
    last if ( $input =~ /^$/ );
    chomp $input;
    push @lines, $input;
}
for ( my $i = 0; $i < scalar @lines; $i++ ) {
    if ( $i == 0 ) {
        ( $a, $b, $c ) = split( / /, $lines[$i] );
    }
    if ( $i == 1 ) {
        $numtrains = $lines[$i];
    }
    else {
        my @time = split( / /, $lines[$i] );
        push @trscd, $time[0] * 60 + $time[1];
    }
}
shift @trscd;
for ( my $j = 0; $j < scalar @trscd; $j++ ) {
    $startTime  = $trscd[$j] - $a;
    $arriveTime = $trscd[$j] + $b + $c;
    my $h = int( $arriveTime / 60 );
    my $m = $arriveTime % 60;
    printf( "$trscd[$j] : $startTime : Arrive at %2.2d:%2.2d\n", $h, $m );

    if ( $arriveTime > $timeLimit ) {
        $startTime = $trscd[ $j - 1 ] - $a;
        my $hs = int( $startTime / 60 );
        my $ms = $startTime % 60;
        printf( "%2.2d:%2.2d\n", $hs, $ms );
        last;
    }
}
$startTime = $trscd[ $numtrains - 1 ] - $a;
my $hs = int( $startTime / 60 );
my $ms = $startTime % 60;
printf( "%2.2d:%2.2d\n", $hs, $ms ) unless ( $arriveTime > $timeLimit );

__DATA__
10 50 10
6
5 0
6 0
7 15
7 30
7 49
8 00
