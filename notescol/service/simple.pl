#!/usr/bin/perl

use warnings;
use strict;
use AnyEvent;
use AnyEvent::Util;
use IO::Socket::INET;
use MIME::Base64;
use Term::ANSIColor qw(:constants);

$AnyEvent::Util::MAX_FORKS = 31;

my %global_user_db = ();
my $localip   = $ARGV[0];

my $server = IO::Socket::INET->new(
        'Proto'     => 'tcp',
        'LocalAddr' => $localip,
        'LocalPort' => 0x4014,
        'Listen'    => 3,
        'ReuseAddr' => 1
    ) or die $!;

my $cv = AnyEvent->condvar;

my $handle_client = AnyEvent->io(
        fh      => \*{$server},
        poll    => 'r',
        cb      => sub {
            $cv->begin();
            fork_call \&handle_connections, $server->accept, \&handle_token;
        }
    );


sub welcome_msg($) {
    my $client = shift;

    print $client BRIGHT_BLUE."Welcome to the 'Notes collection' service!\n",
                              "Possible actions now are : auth, reg, help\n",
                        RESET."\$ ";
}

sub parse_user_credentials($) {
    my $response = shift;

    my ($plain_token_data, $plain_user_name) = unpack "H32H*", decode_base64($response);
    my ($user_token, $user_name) = ("", "");

    map $user_token.= chr hex, (map $_, $plain_token_data =~ /(..)/g);
    map $user_name .= chr (hex ^ 0xBB), reverse (map $_, $plain_user_name =~ /(..)/g);

    $user_name =~ s/[^|\w ]//g;

    ($user_name, $user_token);
}

sub get_user_info($) {
    my $client = shift;

    print $client BRIGHT_BLUE."--> Now send me your token\n".RESET."# ";
    my $user_token = <$client>;
    
    if (not defined $user_token) {
        return (undef, undef);
    }

    if (scalar(split //, $user_token) < 0x14) {
        return (undef, undef);
    }

    chomp $user_token;
    parse_user_credentials($user_token);
}

sub check_user_id($) {
    my $client = shift;

    my ($user_name, $token_id) = get_user_info($client);

    if (not defined $user_name or not defined $token_id) {
        return undef;
    }

    if (not exists $global_user_db{$user_name}) {
        return undef;
    }

    if ($global_user_db{$user_name} ne $token_id) {
        return undef;
    }

    return $user_name;
}

sub get_user_name($) {
    my $client = shift;

    print $client BRIGHT_BLUE."--> Enter your name (5 or more chars)\n".RESET."# ";
    my $user_name = <$client>;

    return undef if not defined $user_name;

    chomp $user_name;
    $user_name =~ s/[^|\w ]//g;

    return undef if length $user_name < 5;

    ($user_name) = $user_name =~ /^(.{5,15}).*/;

    return $user_name;
}

sub generate_user_id($) {
    my $user_name   = shift;
    my @time_values = unpack "(H2)*", time;

    srand int(hex $time_values[6] * hex $time_values[7]);

    my $user_id = "";

    map $user_id.=chr(int(rand(255)) ^ ord((split //, $user_name)[$_ % length $user_name])), (0 .. 15);

    $user_id;
}

sub create_new_user($) {
    my $client = shift;

    my $user_name = get_user_name($client);

    if (not defined $user_name) {
        print $client RED."--> Wrong user name\n".RESET;
        return (undef, undef, undef);
    }

    if (exists $global_user_db{$user_name}) {
        print $client RED."--> User already exist\n".RESET;
        return (undef, undef, undef);
    }

    my $user_id    = generate_user_id($user_name);
    my $user_token = $user_id.join "", map chr(hex ^ 0xBB), reverse (unpack("H*", $user_name) =~ /(..)/g);   

    return ($user_id, $user_name, $user_token);
}

sub handle_unauth_cmd($$$) {
    my ($client, $cmd, $state) = @_;

    if ($cmd =~ /^auth$/) {
        my $user_name = check_user_id($client);

        if (not defined $user_name) {
            print $client RED."--> Wrong token\n".RESET;
            return undef;
        }

        print $client BRIGHT_BLUE."Hello $user_name\n".RESET;

        $$state{auth} = 1;
        $$state{name} = $user_name;

        return $user_name;
    }

    if ($cmd =~ /^reg$/) {
        my ($user_id, $user_name, $user_token) = create_new_user($client);

        if (not defined $user_name or not defined $user_id or not defined $user_token) {
            print $client RED."--> New account was not created\n".RESET;
            return undef;
        }

        $$state{auth}     = 1;
        $$state{name}     = $user_name;
        $$state{token_id} = $user_id;

        print $client BRIGHT_BLUE."--> Your token is ".encode_base64($user_token).RESET;

        return $user_name;
    }

    if ($cmd =~ /^h[elp]*$/) {
        print $client BRIGHT_BLUE."Currently you are not authenticated thus\n",
                                  "you've access only to the following options :\n",
                                  "=> auth - authenticate yourself\n",
                                  "=> reg  - create new user\n",
                                  "=> help - show this message\n".RESET;
        return undef;
    }

    print $client RED."Unknown command\n".RESET;
}

sub get_file_content($) {
    my $file_name = shift;

    local $/ = undef;
    open my $fh, "$file_name" or return undef;
    my $file_content = <$fh>;
    close $fh;

    if (not defined $file_content) {
        return undef;
    }

    if (length $file_content == 0) {
        return undef;
    }

    $file_content;
}

sub get_user_note($) {
    my $client = shift;

    print $client BRIGHT_BLUE, "Enter your note :\n".RESET."# ";
    my $user_note = <$client>;

    if (not defined $user_note) {
        return undef;
    }

    chomp $user_note;
    $user_note =~ s/[^\w ?!'".,-_]//g;

    if (length $user_note == 0) {
        return undef;
    }

    $user_note;
}

sub write_note_into_file($$) {
    my ($file_name, $note) = @_;

    open my $fh, ">> $file_name" or return undef;
    print $fh $note."\n";
    close $fh;
}

sub handle_auth_cmd($$$) {
    my ($client, $cmd, $state) = @_;

    if ($cmd =~ /^read$/) {
        my $file_content = get_file_content($$state{name});

        if (not defined $file_content) {
            print $client BRIGHT_BLUE."You don't have any notes\n".RESET;
            return undef;
        }

        print $client BRIGHT_BLUE."Your notes :\n".$file_content.RESET;

        return undef;
    }

    if ($cmd =~ /^add$/) {
        my $note = get_user_note($client);

        if (not defined $note) {
            print $client RED."Something is wrong with your note\n".RESET;
            return undef;
        }

        write_note_into_file($$state{name}, $note);

        print $client BRIGHT_BLUE."Your note : '".join "", ($note =~ /^(.{1,8}).*$/),
                                  length $note > 8 ? "..." : "", "' has been saved\n".RESET;

        return undef;
    }

    if ($cmd =~ /^h[elp]*$/) {
        print $client BRIGHT_BLUE."Hey, $$state{name}! here is your help message :\n",
                                  "=> read  - read all my notes\n",
                                  "=> users - get userlist\n",
                                  "=> help  - show this message\n",
                                  "=> add   - add yet another note\n".RESET;
        return undef;
    }

    if ($cmd =~ /^users$/) {
        print $client BRIGHT_BLUE, scalar(keys %global_user_db) > 0 
                                 ? "Registered users : \n".join "\n", (keys %global_user_db)
                                 : "No one is registered", "\n".RESET;
        return undef;
    }

    print $client RED."Unknown command\n".RESET;
}

sub handle_connections($) {
    my $client = shift;

    print "new connection\n";

    welcome_msg($client);

    my %user_credentials = (auth => 0, name => undef, token_id => undef);

    while (my $client_response = <$client>) {
        next if $client_response eq "\n";

        if ($user_credentials{'auth'} == 0) {
            handle_unauth_cmd($client, $client_response, \%user_credentials);
            next;
        }

        if ($user_credentials{'auth'} == 1) {
            handle_auth_cmd($client, $client_response, \%user_credentials);
            next;
        }
    } continue {
        print $client $user_credentials{auth} == 1 ? $user_credentials{name}." " : "","\$ ";
    }

    $cv->end();

    ($user_credentials{name}, $user_credentials{token_id});
}

sub handle_token($$) {
    my ($user_name, $token_id) = @_;
    print "connection was closed\n";

    if (defined $user_name and defined $token_id) {
        $global_user_db{$user_name} = $token_id if not exists $global_user_db{$user_name};
    }
}

$cv->recv();