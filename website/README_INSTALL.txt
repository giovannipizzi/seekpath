1. Put your script as a subfolder of /var/www/ (important, otherwise X-Sendfile does not allow file transfer), give permissions to the user that will be executing! (Create a new one if needed)
2. Install libapache2-mod-wsgi and libapache2-mod-xsendfile
3. activate the modules (with 'sudo a2enmod wsgi' and 'sudo a2enmod xsendfile')
4. run the script ./create_wsgi.py AS THE USER that will run, check that all modules are found.
5. copy the kpath-visualizer-site.conf file to /etc/apache2/sites-available
6. 'sudo a2ensite kpath-visualizer-site'
7. check you can reach http://YOURSERVER/kpath_visualizer



Note: To deploy, we follow the instructions from http://flask.pocoo.org/docs/0.11/deploying/mod_wsgi/
