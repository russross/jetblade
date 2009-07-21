#!/usr/bin/perl -w
use strict;

my $count = 1;
foreach my $file (`ls *png`) {
    chomp $file; 
    my $str = sprintf('%04d', $count);
    `mv $file $str.png`;
    $count++;
}
