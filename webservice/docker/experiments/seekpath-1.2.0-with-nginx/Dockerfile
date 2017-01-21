# Use phusion/baseimage as base image. To make your builds
# reproducible, make sure you lock down to a specific version, not
# to `latest`! See
# https://github.com/phusion/baseimage-docker/blob/master/Changelog.md
# for a list of version numbers.
# Note also that we use phusion because, as explained on the 
# http://phusion.github.io/baseimage-docker/ page, it automatically
# contains and starts all needed services (like logging), it
# takes care of sending around signals when stopped, etc.
##
# Actually, I use passenger-full that already has ngingx and python
# https://github.com/phusion/passenger-docker#using
FROM phusion/passenger-customizable:0.9.19

MAINTAINER Giovanni Pizzi <giovanni.pizzi@epfl.ch>

ARG SEEKPATH_VERSION=1.2.0

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# If you're using the 'customizable' variant, you need to explicitly opt-in
# for features. Uncomment the features you want:
#
    #   Build system and git.
RUN /pd_build/utilities.sh && \
    #   Python support (2.7 and 3.x - it is 3.5.x in this ubuntu 16.04)
    /pd_build/python.sh && \
    # Enable Nginx and passenger
    rm -f /etc/service/nginx/down

##########################################
############ Installation Setup ##########
##########################################

# First, install pip (for python 2)
# install required software
## Note: to install instead pip3 for python3, install the package python3-pip
## However, then one has to configure the web server to use wsgi with python3
RUN apt-get update \
    && apt-get -y install \
    python-pip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean all

# install rest of the packages as normal user (app, provided by passenger)
USER app

# set $HOME
ENV HOME /home/app

# Download code
RUN mkdir -p $HOME/code/
WORKDIR $HOME/code
RUN git clone \
      https://github.com/giovannipizzi/seekpath && \
    cd seekpath && \
    git checkout v$SEEKPATH_VERSION 

# Install SeeK-path
# Note: if you want to deploy with python3, use 'pip3' instead of 'pip'
WORKDIR /home/app/code/seekpath
RUN pip install -U --user pip setuptools && \
    pip install --user -U .[bz,webservice]

# Create empty public dir, needed by passenger
RUN mkdir webservice/public

# Create a proper wsgi file file
#
# NOTE! For the time being, I just disable X-Sendfile,
# that exists only in apache. For nginx, it is called 
# X-Accel-Redirect, requires some changes to the code though
# Note that this means, however, that serving static files 
# will be quite slow
#
ENV SP_WSGI_FILE=webservice/passenger_wsgi.py
RUN echo "import sys" > $SP_WSGI_FILE && \
    echo "sys.path.insert(0, '/home/app/code/seekpath/webservice')" >> $SP_WSGI_FILE && \
    echo "from seekpath_app import app as application" >> $SP_WSGI_FILE && \
    echo "application.use_x_sendfile = False" >> $SP_WSGI_FILE 

# Go back to root.
# Also, it should remain as user root for startup
USER root

# Setup nginx
# Disable default nginx site
RUN rm /etc/nginx/sites-enabled/default
ADD conf/seekpath-nginx.conf /etc/nginx/sites-enabled/seekpath.conf
# Set startup script to create the secret key
RUN mkdir -p /etc/my_init.d
ADD ./conf/create_secret_key.sh /etc/my_init.d/create_secret_key.sh

# Web
EXPOSE 80

