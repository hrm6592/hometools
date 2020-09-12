# FizzBuzz
our $counter;

for ( $counter = 1 ; $counter <= 100 ; $counter++ ) {
    if ( $counter % 3 == 0 ) {
        print "Fizz";
        print "Buzz" if ( $counter % 5 == 0 );
    }
    elsif ( $counter % 5 == 0 ) {
        print "Buzz";
    }
    else {
        print "$counter";
    }
    print  "\n";
}

