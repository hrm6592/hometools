#!/usr/bin/perl
use strict;

our $flag  = 0;
our $count = 0;
our @nums;

open( IN, "-" ) or die;
while ( my $line = <IN> ) {

    # while ( my $line = <DATA> ) {
    chomp $line;

    # print ($line, "\n");
    if ( $line =~ /^\d+$/ ) {

        # First, number of numbers
        $count = $line;

        # print("count : $count\n");
    }
    else {
        @nums = split( / +/, $line );

        # print("count : $count\n");
        # print( "count of nums : ", scalar(@nums), "\n" );

        for ( my $i = 0 ; $i <= $count ; $i++ ) {
            last if ( $nums[$i] !~ /\d+/ );

            # print("$i -> $nums[$i]\n");
            for ( my $j = 0 ; $j <= $count ; $j++ ) {
                next if ( $i == $j );
                last if ( $nums[$j] !~ /\d+/ );

                # print( ( "\t", $nums[$i] + $nums[$j], "\n" ) );
                $flag++ if ( ( $nums[$i] + $nums[$j] ) == 256 );
            }
        }
    }
}

# close(IN);

if ($flag) {
    print "yes";
}
else {
    print "no";
}

exit 0;

__DATA__
11
0 1 2 3 4 5 6 7 8 9 256
