# Zcash Testnet Faucet 

A Django app that dispenses testnet TAZ to transparent and shielded addresses. Accepts donations as well.

## Initial setup instructions:  

Install dependencies:
```
sudo apt-get install libpq-dev python-dev postgresql postgresql-contrib python-psycopg2 nginx fail2ban
```

After cloning the repo for zfaucet, be sure to clone the pyZcash library (contains wrappers around zcash-cli rpc calls and a few custom functions):

Create a subdirectory for the lib. From `/home/{{ faucet_user }}/faucet`:
```
mkdir lib
chmod 0755 lib 
cd lib
git clone https://github.com/arcalinea/pyZcash
```
From `/home/{{ faucet_user }}/faucet`, create a symlink to the lib:
`ln -s lib/pyZcash/pyZcash pyZcash`

## Configuring Django

Modify settings.py to configure settings.  

Enter DB secrets:
```
DJANGO_SECRET_KEY=xxx
DJANGO_POSTGRESQL_PASSWORD=xxx
```
Set 'dev' or 'prod' mode for development or production: `DJANGO_ENVIRONMENT=prod`

Install the requirements in requirements.txt:
```
pip install -r requirements.txt  
pip install -r requirements-prod.txt  
```
Create a user "postgres" and create a database named "django":
```
sudo su - postgres  
createdb django  
createuser -P django  
```
Enter the postgres shell and grant privileges on the django db to django:
```
psql  
GRANT ALL PRIVILEGES ON DATABASE django TO django;
```
Make the migrations for the django db:
```
python manage.py makemigrations
python mange.py migrate
```

## Configuring the webserver

Set up nginx and Gunicorn:

```
gunicorn --workers=2 zfaucet.wsgi  
sudo service nginx start  
vim /etc/nginx/sites-available/zfaucet 
```

    server {
        server_name faucet.yoursite.com;

        access_log off;

        location /static/ {
       		alias /home/{{ faucet_user }}/faucet/faucet/static/;
    	}

        location / {
        	proxy_pass http://127.0.0.1:8000;
        	proxy_set_header Host $host;
        	proxy_set_header X-Forwarded-Host $server_name;
       		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       		proxy_set_header X-Real-IP $remote_addr;
        	add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
    	}
    }

Enable the nginx config for zfaucet and remove the default config:
```
cd /etc/nginx/sites-enabled  
sudo ln -s ../sites-available/zfaucet  
sudo rm default
```

Collect the static resources for the Django app. 

Make sure path to static resources in settings.py is set to the same location specified in the nginx config.
In settings.py, set `STATIC_ROOT = '/home/{{faucet_user}}/faucet/faucet/static'`

Then from within `/home/{{ faucet_user }}/faucet/`, run command: `python manage.py collectstatic`

Set up fail2ban to rate-limit requests for the faucet. Put the following in `/etc/fail2ban/filter.d/zcash-faucet.conf`:
```
# Fail2ban filter for Zcash faucet
[Definition]

failregex = ^ -.*POST / HTTP/1\.." 200
ignoreregex =
```
And append this block within `/etc/fail2ban/jail.local`:
```
      [zcash-faucet]

      enabled  = true
      filter   = zcash-faucet
      port     = http,https
      action   = iptables-multiport[name=zcash-faucet, port="http,https"]
      logpath  = /var/log/nginx/access.log
      maxretry = 10
      findtime = 3600
      bantime  = 86400
```
  
## Setting up custom functions

Create a cron job for a regular faucet health check to collect wallet/network stats, and to sweep coinbase funds into a zaddr:

crontab -e  
*/5 * * * * python /home/{{faucet_user}}/faucet/manage.py healthcheck 
*/5 * * * * python /home/{{faucet_user}}/faucet/manage.py sweepfunds

Make sure you run the healthcheck before starting the server so the database has at least one entry.
 
