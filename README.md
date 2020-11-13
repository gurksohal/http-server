# http-server

The server can be run by using the following command
python server.py

Once the server is running visit http://localhost:15093/

Supports retrieving static files, and executing other python scripts on the server.


http://localhost:15093/test - retrieve index.html in the test directory

http://localhost:15093/test/script.py - executes the python script with the correct body, and query params

