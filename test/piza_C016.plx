#!/usr/bin/perl
#
%leet = (
    'A' => 4,
    'E' => 3,
    'G' => 6,
    'I' => 1,
    'O' => 0,
    'S' => 5,
    'Z' => 2,
);
our $input;
$input = <>;
chomp $input;
@ary_input = split( //, $input );
for ( my $i = 0 ; $i <= scalar @ary_input ; $i++ ) {

    # print "$ary_input[$i],";
    my $output =
      ( exists $leet{ $ary_input[$i] } )
      ? $leet{ $ary_input[$i] }
      : $ary_input[$i];
    print $output;
}
print "\n";
