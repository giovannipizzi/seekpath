#!/usr/bin/env python
import os
import sys
import importlib
from collections import defaultdict
import string

import getpass, grp, pwd

WSGI_FILENAME = 'seekpath_app.wsgi'
site_fname = "seekpath-site.conf"

current_user = getpass.getuser()
current_group = grp.getgrgid(pwd.getpwnam(current_user).pw_gid).gr_name

#servername = raw_input("Please insert the server name: ")
#servername = "theospc7.epfl.ch"

print("I am going to configure everything running as user '{}' and "
      "group '{}'".format(current_user, current_group))
#print "and the server name will be '{}'".format(servername)
print " Continue? [CTRL+C to stop]"
raw_input()

content_lines = []
content_lines.append("import sys")
wsgi_folder = os.path.split(os.path.realpath(__file__))[0]
content_lines.append("sys.path.insert(0, '{}')".format(wsgi_folder))
wsgi_file = os.path.join(wsgi_folder, WSGI_FILENAME)

import_content_lines = defaultdict(list)
for package in ['flask', 'numpy', 'scipy', 'ase', 'spglib', 'seekpath']:
    # Get the path
    try:
        m = importlib.import_module(package)
        import_content_lines["sys.path.append('{}')".format(
            os.path.realpath(
                os.path.join(os.path.split(m.__file__)[0],
                             os.pardir)))].append(package)
    except ImportError:
        raise ValueError(
            "Unable to load {}, put it in the python path!".format(package))
for importline, modules in import_content_lines.iteritems():
    content_lines.append("{} # {}".format(importline, ", ".join(modules)))
content_lines.append("")
content_lines.append("from seekpath_app import app as application")

print "=" * 78
print "\n".join(content_lines)
print "=" * 78
print "This is the content I want to write in the {} file.".format(
    WSGI_FILENAME)
print "Can I continue? [CTRL+C to stop]"
raw_input()

with open(WSGI_FILENAME, 'w') as f:
    f.write("\n".join(content_lines))

print "File {} written.".format(WSGI_FILENAME)

site_template = string.Template("""
    WSGIDaemonProcess $appname user=$user group=$group threads=$numthreads
    WSGIScriptAlias $urlpath $wsgipath

    XSendFile On
    XSendFilePath $wsgifolder/static/

    <Directory $wsgifolder>
        WSGIProcessGroup $appname
        WSGIApplicationGroup %{GLOBAL}
        ## Next two lines for apache < 2.4
        #Order deny,allow
        #Allow from all
        ## Next lines for apache >= 2.4
        Require all granted
    </Directory>
""")

site_file_content = site_template.substitute(
    #    servername=servername,
    appname="seekpath_app",
    user=current_user,
    group=current_group,
    numthreads=4,
    urlpath='/seekpath',
    wsgipath=wsgi_file,
    wsgifolder=wsgi_folder,
)

print "=" * 78
print site_file_content
print "=" * 78
print "This is the content I want to write in the {} file.".format(site_fname)
print "Can I continue? [CTRL+C to stop]"
raw_input()

with open(site_fname, 'w') as f:
    f.write(site_file_content)

print "File {} written.".format(site_fname)
