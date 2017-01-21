This folder contains 
1. ``seekpath``: a Dockerfile for installing seekpath and the web service.
      This is deployed with apache2 as a webserver.
      Also, this has some hooks to work in conjunction with automated builds
      of Docker Hub, also from a fork and working for the correct commit.
2. ``seekpath-webservice``: a docker-compose file to start it.
      Note that it will use the image uploaded on Dockerhub, rather than
      building from the Dockerfile.
3. ``experiments``: contains various experiments, in particular 
      seekpath deployed with nginx (but without any x-sendfile support, 
      so serving static files might be slow)
