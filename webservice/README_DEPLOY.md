Notes on how to deploy the seekpath web service
-----------------------------------------------

This folder in currently not installed when you do 
`pip install seekpath`.

First step: install dependencies:

  pip install --user -r ../optional_requirements.txt

Then:

1. Put your script as a subfolder of `/var/www/` (important, otherwise 
   `X-Sendfile` does not allow file transfer), and give permissions to the 
   user that will be executing! (Create a new one if needed)
2. Install `libapache2-mod-wsgi` and `libapache2-mod-xsendfile`
3. Activate the modules (with `sudo a2enmod wsgi` and `sudo a2enmod xsendfile`)
4. Run the script `./create_wsgi.py` AS THE USER that will run, check that all 
   modules are found.
5. Copy the `seekpath-site.conf` file to `/etc/apache2/sites-available`
6. Run sudo `a2ensite seekpath-site`
7. check you can reach http://YOURSERVER/seekpath/

Note: To deploy, we follow the instructions from 
http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/

Forwarding the traffic through a different machine
--------------------------------------------------

This happens when you want to use e.g. a reverse proxy, e.g.
website on a hidden machine in the local network, 
proxied by a machine visible from the outside. For instance, if you
run seekpath in a Docker container and want to show it by proxying it
via your main Apache server.

1. Enable modules `proxy` and `proxy_http` (more modules needed if you want to 
   proxy https requests). Moreover, add also the `headers` module if you 
   want to proxy seekpath to a subdomain (see below).

2. Add the following to your site. **Note**: in the following, we want to proxy 
   the web service at the address `http://mymachine/proxied`, 
   and the actual seekpath service runs on `localhost` at port `4444`; 
   of course, adapt as needed:

   ```
   ProxyRequests off
   ProxyPreserveHost off

   <Location /proxied>
       ProxyPass http://localhost:4444/
       ProxyPassReverse http://localhost:4444/
       RequestHeader set X-Script-Name /proxied
       RequestHeader set X-Scheme http
       Order deny,allow
       Allow from all
   </Location>
   ```

  For nginx, similar headers need to be set, see 
  http://flask.pocoo.org/snippets/35/ 
  (something similar to the following, untested):

    location /proxied {
        proxy_pass http://localhost:4444;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /proxied;
        }

   **Technical note**: The important header to set is `X-Script-Name`, 
   that is used in the `ReverseProxied` class inside `seekpath_app.py`
   to properly set the script name, and therefore generate correct
   redirect URLs. Otherwise, redirects like
   `return flask.redirect(flask.url_for('input_structure'))` would not
   prepend `/proxied/` to the URL.

