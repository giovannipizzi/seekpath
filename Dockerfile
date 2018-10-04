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
# Actually, I use passenger-full that already has python
# https://github.com/phusion/passenger-docker#using
FROM phusion/passenger-customizable:0.9.19

MAINTAINER Giovanni Pizzi <giovanni.pizzi@epfl.ch>

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

# If you're using the 'customizable' variant, you need to explicitly opt-in
# for features. Uncomment the features you want:
#
    #   Build system and git.
    #   Python support (2.7 and 3.x - it is 3.5.x in this ubuntu 16.04)
RUN /pd_build/utilities.sh && \
    /pd_build/python.sh 

##########################################
############ Installation Setup ##########
##########################################

# Install required software

# Install Apache (nginx doesn't have the X-Sendfile support
# that we use)
## Here and below we install everything with python3
RUN apt-get update \
    && apt-get -y install \
    python3-pip \
    apache2 \
    libapache2-mod-xsendfile \
    libapache2-mod-wsgi-py3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean all

# set $HOME
ENV HOME /home/app

# Download code
RUN mkdir -p $HOME/code/seekpath
WORKDIR $HOME/code/seekpath

# Actually, don't download, but get the code directly from this repo
COPY ./seekpath/ seekpath
COPY ./webservice/ webservice
COPY ./setup.py setup.py
COPY ./README.rst README.rst
COPY ./MANIFEST.in MANIFEST.in
COPY ./LICENSE.txt LICENSE.txt
COPY ./run_tests.py run_tests.py
COPY ./optional-requirements.txt optional-requirements.txt

# Set proper permissions
RUN chown -R app:app $HOME

# Run this as sudo to replace the version of pip
RUN pip3 install -U 'pip>=10' setuptools wheel

# install rest of the packages as normal user (app, provided by passenger)
USER app

# Install SeeK-path
# Note: if you want to deploy with python3, use 'pip3' instead of 'pip'
WORKDIR /home/app/code/seekpath
# First install pinned versions of packages
RUN pip3 install --user -r optional-requirements.txt --only-binary numpy,scipy
# Then install the code without extra dependencies
RUN pip3 install --user .

# Create a proper wsgi file file
#
ENV SP_WSGI_FILE=webservice/seekpath_app.wsgi
RUN echo "import sys" > $SP_WSGI_FILE && \
    echo "sys.path.insert(0, '/home/app/code/seekpath/webservice')" >> $SP_WSGI_FILE && \
    echo "from seekpath_app import app as application" >> $SP_WSGI_FILE 

# Go back to root.
# Also, it should remain as user root for startup
USER root

# Setup apache
# Disable default apache site, enable seekpath site; also 
# enable needed modules
ADD ./.docker_files/seekpath-apache.conf /etc/apache2/sites-available/seekpath.conf
RUN a2enmod wsgi && a2enmod xsendfile && \
    a2dissite 000-default && a2ensite seekpath 

# Activate apache at startup
RUN mkdir /etc/service/apache
ADD ./.docker_files/apache_run.sh /etc/service/apache/run

# Set startup script to create the secret key
RUN mkdir -p /etc/my_init.d
ADD ./.docker_files/create_secret_key.sh /etc/my_init.d/create_secret_key.sh

# Web
EXPOSE 80

# Final cleanup, in case it's needed
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*