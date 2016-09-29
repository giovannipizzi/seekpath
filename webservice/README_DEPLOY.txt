A note: this folder in currently not installed when you do 
'pip install seekpath'

First step: 
- Install with sudo pip install 'seekpath[bz,webservice]'
Then:

1. Put your script as a subfolder of /var/www/ (important, otherwise X-Sendfile
   does not allow file transfer), give permissions to the user that will be 
   executing! (Create a new one if needed)
2. Install libapache2-mod-wsgi and libapache2-mod-xsendfile
3. activate the modules (with 'sudo a2enmod wsgi' and 'sudo a2enmod xsendfile')
4. run the script ./create_wsgi.py AS THE USER that will run, check that all 
   modules are found.
5. copy the seekpath-site.conf file to /etc/apache2/sites-available
6. 'sudo a2ensite seekpath-site'
7. check you can reach http://YOURSERVER/seekpath/



Note: To deploy, we follow the instructions from 
http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/



NOTE ON FORWARDING THE TRAFFIC THROUGH A DIFFERENT MACHINE (reverse proxy, e.g.
website on a hidden machine in the local network, proxied by a machine visible
from the outside):

1. enable mods proxy and proxy_http (more modules needed if you want to 
   proxy https requests...)

2. Add the following to your site:

        ProxyRequests off
        ProxyPreserveHost off

        <Proxy *>
                Order deny,allow
                Allow from all
        </Proxy>

        ProxyPass /seekpath/ http://INTERNALMACHINE/seekpath/
        ProxyPassReverse /seekpath/ http://INTERNALMACHINE/seekpath/

