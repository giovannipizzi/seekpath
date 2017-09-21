This folder is created to be able to upload a pip cache into the docker image to speed up builds.
Empty by default, it does nothing. If however it is populated with a valid pip cache before 'docker build', it can speed up significantly the build process.
