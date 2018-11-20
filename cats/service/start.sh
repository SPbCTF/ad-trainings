killall python 2> /dev/null
ip_host=`ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}'`
python manage.py runserver $ip_host:8000 > /dev/null &
