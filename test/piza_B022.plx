#!/usr/bin/perl
#
our $m, $n, $k;
our @lines, @numsp;
while ( ( my $input = <DATA> ) !~ /^$/ ) {
    last if ( $input =~ /^$/ );
    chomp $input;
    push @lines, $input;
}
for ( my $i = 0; $i < scalar @lines; $i++ ) {
    if ( $i == 0 ) {
        ( $m, $n, $k ) = split( / /, $lines[$i] );
        $numsp[0] = $n;
    }
    else {
        for ( my $j = 1; $j <= $m; $j++ ) {
            if ( $j == $lines[$i] ) {
                $numsp[$j]++ if ( $numsp[0] > 0 );
                $numsp[0]--;
            }
            else {
                $numsp[$j]--;
                if ( $numsp[$j] < 0 ) {
                    $numsp[$j] = 0;
                }
                else {
                    $numsp[ $lines[$i] ]++;
                }
            }
        }
    }
}
shift @numsp;

our $max;
foreach my $x (@numsp) {
    $max = $x if ( $x > $max );
}
for ( my $y = 0; $y < scalar @numsp; $y++ ) {
    print $y+ 1, "\n" if ( $numsp[$y] == $max );
}
__DATA__
3 3 4
1
1
2
3
