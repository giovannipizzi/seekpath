This is a preliminary test to have a Dockerfile with seekpath running with
nginx.
It works, but it cannot use x-sendfile (as nginx uses a different approach
with x-accel, but it's not implemented in flask, so would require some work)
so serving static files might be slow.
