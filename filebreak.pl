#!/usr/bin/perl

# Modified code to open a file and modify instead of in terminal

if (($ARGV[0] cmp 'reviews.txt') == 0) {
  my $filename = 'RawData/' . $ARGV[0];
  open (data, $filename) or die;
} else {
  my $filename = 'Sorted/' . $ARGV[0];
  open (data, $filename) or die;
}

my $newfilename = 'Formatted/formatted_' .  $ARGV[0];
open(my $newdata, '>',$newfilename) or die;

while (<data>) {
  chomp;
  if (/^([^,]+),(.*?)$/) {
    $key=$1; $rec=$2;
    $key =~ s/\\/&92;/g;
    $rec =~ s/\\/&92;/g;
    print $newdata $key, "\n", $rec, "\n";
  }
}

close($data);
close($newdata);
