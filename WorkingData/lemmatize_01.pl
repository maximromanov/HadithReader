#!/usr/bin/perl
use strict;
use LWP::UserAgent;
use Encode;
use JSON;
use Data::Dumper;

# uses the Bamboo morphology service to parse the words for their lemmas

my $text=$ARGV[0];
my $service_url = "http://services.perseids.org/bsp/morphologyservice/analysis/word?engine=aramorph&lang=ara&word=WORD";
my $ua = new LWP::UserAgent();
$ua->default_header('Accept', 'application/json');
my $json = JSON->new->allow_nonref;



open(TEXT, $text) || die "can't open $text";

my %hash=();

while (<TEXT>) {
    my $line = $_;
    chomp $line;
    $line =  decode("UTF-8",$line);
    # get rid of beginning and trailing spaces
    $line =~ s/^\s+//;    
    $line =~ s/\s+$//;    
    # get rid of final period
    $line =~ s/\.$//;

    # tokenize on spaces
    my @words=split /\s+/, $line;

    # iterate through the words and submit to morph service
    foreach my $word(@words) {
        # only look it up if we haven't already encountered the word
	unless (exists $hash{$word}) {
            my $url = $service_url;
            $url =~ s/WORD/$word/;
            my $resp = $ua->get($url);

            unless ($resp->is_success)
            {
                die "Unable to parse $word: @{[$resp->status_line]}\n";
            }
            # get the headword
            my @lemmas = get_hdwds($json->decode($resp->decoded_content));
            if (scalar @lemmas) {
                $hash{$word} = join ',', @lemmas;
            } else {
                $hash{$word} = 'NOTFOUND';
            }
        }
        print  encode("UTF-8","$word\t$hash{$word}\n");
    }
}

sub get_hdwds {
    my ($decoded) = shift;
    my %hdwds;
    if (ref($decoded) eq 'HASH'
        && $decoded->{'RDF'}
        && ref($decoded->{'RDF'}{'Annotation'} ) eq 'HASH'
       )
    {
        my @entries;
        # only one parse
        if (ref($decoded->{'RDF'}{'Annotation'}{'Body'}) eq 'HASH') {
            push @entries, $decoded->{'RDF'}{'Annotation'}{'Body'}{'rest'}{'entry'};
        # multiple parses
        } elsif (ref($decoded->{'RDF'}{'Annotation'}{'Body'}) eq 'ARRAY') {
            foreach my $body (@{$decoded->{'RDF'}{'Annotation'}{'Body'}}) {
                push @entries, $body->{'rest'}{'entry'};
            }
        }
        foreach my $entry (@entries) {
            # one dictionary entry
            if (ref($entry) eq 'HASH') {
                my $dict = $entry->{'dict'};
                if ($dict) {
                    if (ref($dict) eq 'ARRAY') {
                        warn "array\n";
                        $hdwds{decode("UTF-8",$dict->[0])} = 1;
                    } elsif (ref($dict) eq 'HASH') {
                        $hdwds{decode("UTF-8",$dict->{'hdwd'}{'$'})} = 1;
                    }
                }
                else {
                    warn "plain\n";
                    $hdwds{decode("UTF-8",$dict)} = 1;
                }
            }
        }
    }
    return keys %hdwds;
}

