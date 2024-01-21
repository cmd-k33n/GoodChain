Requires an X Server like: https://sourceforge.net/projects/vcxsrv/ on Windows.
Adjust the ENV variable DISPLAY in Dockerfile to point to the ip-address for your own X Server.

To launch the test setup build the Dockerfile and then run `docker compose up`.
