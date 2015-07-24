almasales
========

This system is used to organise, automate and synchronise all of the customer facing areas within your company: from marketing to sales to customer service


### How to start the project

### Dependencies

PyLibMC - client for working with Memcached protocol

```
sudo apt-get install sudo apt-get install -y libmemcached-dev zlib1g-dev libssl-dev python-dev build-essential build-dep python-psycopg2
```

```
virtualenv --no-site-packages alma.net
cd alma.net
. ./bin/activate
mkdir alma.net
cd alma.net
git init .
git remote add origin git@github.com:Mafioso/alma.net.git
git pull origin develop
pip install -r requirements.txt
cd src
./manage.py syncdb
./manage.py migrate
./manage.py runserver localhost:8000

```

### How to launch test suite

```
nose2 # run from dir where manage.py is located
nose2 -v --with-cov --cov-config coverage.cfg


# functional (view, selenium)
DJANGO_CONFIGURATION=TestConfiguration ./manage.py test --verbosity=3 --configuration=TestConfiguration --liveserver=0.0.0.0:8000

# unit
```

### hosts configurations

```
sudo nano /etc/hosts
127.0.0.1    alma.net
127.0.0.1    bwayne.alma.net
127.0.0.1    my.alma.net

create default user and company
(email: b.wayne@batman.bat, password:123, company subdomain: bwayne):
./manage.py createdefaultuser
```


```
To execute tests on test server using selenium you need to create configuration file in your system
mkdir ~/.almanet
cd ~/.almanet
nano almanet.conf.py

HOSTCONF_REGEX = r'alma1\.net:8000'
PARENT_HOST = 'alma1.net:8000'
SESSION_COOKIE_DOMAIN = '.alma1.net'
SITE_DOMAIN = PARENT_HOST

put this config to almanet.conf.py file. After this you need to connect to vpn and write on test server host file your vpn ip and your domain
```

Integrate browserify project with Django
----------------------------------------

1. Create local file for settings overriding
```touch ~/.almanet/almanet.conf.py```

2. Update it by setting directory to your browserify project
```STATICFILES_DIRS = '+/home/anguix/work/projects/alma.net/frontend/almanet-frontend```

Attention: '+' indicates add it to original STATICFILES_DIRS. The final constant will look like:
```
('/home/anguix/work/projects/alma.net/alma.net/alma.net/src/static',
 '/home/anguix/work/projects/alma.net/frontend/almanet-frontend')
 ```


Restore from dump
-----------------

1. Drop database: `dropdb almanet`
2. Create database:
  2.1 `sudo -u postgres psql`
  2.2 `CREATE DATABASE almanet WITH OWNER = xepa4ep ENCODING = 'UTF-8'`
  2.3 test session - `sudo -u postgres psql -d almanet`
3. Grant all privilleges
  3.1 `sudo -u postgres psql -d almanet`
  3.2 `GRANT ALL ON SCHEMA PUBLIC TO almanet`
  3.3 check permissions - `\dn+`
4. Restore data
  4.1 `sudo -u postgres psql -U xepa4ep -d almanet -W -f dbdumps/almanet.sql`
5. Post restore
  5.1 enter postres user mode - `su postgres`
  5.2 execute post restore script - `./postgres_restore_post.sh almanet xepa4ep`


MAC OSX deps
-----------

Memcached (pylibmc) -- `brew install libmemcached`

Load postgres libraries into path, for ex for Postgres 9.4
`sudo ln -sf /Library/PostgreSQL/9.4/lib/YOUR_LIB.dylib /usr/lib`


Start uwsgi on dev:
uwsgi --ini uwsgi.ini --check-static /Users/rustem/projects/almacloud/alma.net/src --static-map /static=/Users/rustem/projects/almacloud/almanet-frontend/