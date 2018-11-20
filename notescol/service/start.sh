killall perl 2> /dev/null
ip_host=`ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}'`
perl simple.pl $ip_host > /dev/null &
