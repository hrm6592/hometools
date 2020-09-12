#!/usr/bin/perl
#
our $input_num;

$input_num = <>;
chomp $input_num;

exit if ($input_num !~/\d+/);

print "*" x $input_num, "\n";
