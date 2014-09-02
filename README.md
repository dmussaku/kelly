alma.net
========

This system is used to organise, automate and synchronise all of the customer facing areas within your company: from marketing to sales to customer service


### How to start the project

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

for pylibmc dependencies
sudo apt-get install sudo apt-get install -y libmemcached-dev zlib1g-dev libssl-dev python-dev build-essential
