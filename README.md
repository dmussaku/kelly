alma.net
========

This system is used to organise, automate and synchronise all of the customer facing areas within your company: from marketing to sales to customer service


### How to start the project

### Dependencies

PyLibMC - client for working with Memcached protocol

```
sudo apt-get install sudo apt-get install -y libmemcached-dev zlib1g-dev libssl-dev python-dev build-essential
```

```
virtualenv --no-site-packages alma.net
cd alma.net
. ./bin/activate
mkdir alma.net
git init .
git remote add origin git@github.com:Mafioso/alma.net.git
git pull origin develop
pip install -r requirements.txt
cd src
./manage.py syncdb
./manage.py runserver localhost:8000

```

### How to launch test suite

```
nose2 # run from dir where manage.py is located
nose2 -v --with-cov --cov-config coverage.cfg
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