#!/usr/bin/perl
#
our $input_num, $input, $output;
our @lines;
$input_num = <>;
chomp $input_num;
for ( my $i = 0; $i <= $input_num; $i++ ) {
    $input = <>;
    chomp $input;
    push @lines, $input;
}
foreach (@lines) {
    last if ( $_ =~ /^$/ );
    if ( $_ =~ /^(\w+?)(s|sh|ch|o|x)$/ ) {
        $output = $_ . "es";
    }
    elsif ( $_ =~ /^(\w+?)(f|fe)$/ ) {
        $output = $1 . "ves";
    }
    elsif ( ( $_ =~ /^(\w+?)([^aiueo])y$/ ) ) {
        $output = $1 . $2 . "ies";
    }
    else {
        $output = $_ . "s";
    }
    print "$output\n";
}
