import socket
import os
import subprocess as process


# return requested file
def getFile(path):
    # if the file exists, return it
    if os.path.isfile(path):
        f = open(path)
        return f
    # if the current path is a directory, find index.html within and return it
    elif os.path.isdir(path):
        path = path + "/index.html"
        if os.path.isfile(path):
            f = open(path)
            return f


# generate servers response, if a static file has been requested
def generateResponse(rFile, method, path):
    serverResponse = ""
    if rFile is not None:
        # get the extension of the requested file
        extension = os.path.splitext(rFile.name)[1]
        # determine content type
        if extension == ".html":
            extension = "html"
        else:
            extension = "plain"

        serverResponse += "HTTP/1.1 200 OK\n"
        serverResponse += "Content-Length: {}\n".format(os.path.getsize(rFile.name))
        serverResponse += "Content-Type: text/{}\n\n".format(extension)

        # if request method wasn't head, include the contents of the file in response
        if method != "HEAD":
            serverResponse += "".join(rFile.readlines())
    else:  # requestFile is None
        serverResponse += "HTTP/1.1 404 Not Found\n"
        serverResponse += "Content-Type: text/plain\n\n"

        if method != "HEAD":
            if path.rfind('.') == -1:  # path indicates user requested a directory
                serverResponse += "index.html not found within requested directory \"/{}\"".format(path)
            else:  # requested a file
                serverResponse += "requested resource \"/{}\" not found".format(path)

    return serverResponse


def getHeaders(request):
    headers = {}
    line = request.readline().strip()
    # while line isn't empty
    while line:
        if len(line.split(":", 1)) == 2:
            name, value = line.split(":", 1)
            headers[name] = value.strip()  # store the headers in a map
        else:
            print("Incorrect header format")
            return None
        line = request.readline().strip()
    return headers


def getBody(request, headers):
    body = None
    # get content length from request headers, if no length was provided, default to zero
    size = headers.get("Content-Length", 0)
    if size != 0:
        body = request.read(int(size))
    return body


def removeVars():
    if "HTTP_COOKIE" in os.environ:
        os.environ.pop("HTTP_COOKIE")

    if "CONTENT_LENGTH" in os.environ:
        os.environ.pop("CONTENT_LENGTH")

    if "CONTENT_TYPE" in os.environ:
        os.environ.pop("CONTENT_TYPE")

    if "REQUEST_METHOD" in os.environ:
        os.environ.pop("REQUEST_METHOD")

    if "QUERY_STRING" in os.environ:
        os.environ.pop("QUERY_STRING")


# set the environ variables
def createVars(headers, method, path):
    for name in headers:
        if name == "Cookie":
            os.environ["HTTP_COOKIE"] = headers[name]
        elif name == "Content-Length":
            os.environ["CONTENT_LENGTH"] = headers[name]
        elif name == "Content-Type":
            os.environ["CONTENT_TYPE"] = headers[name]
    os.environ["REQUEST_METHOD"] = method
    if len(path.split('?')) == 2:
        os.environ["QUERY_STRING"] = path.split('?')[1]


def handleScript(path, headers, body, method):
    createVars(headers, method, path)
    path = path.split('?')[0]
    pInput = body

    procObject = process.Popen(["python", path], stdin=process.PIPE, stdout=process.PIPE, stderr=process.PIPE,
                               universal_newlines=True)
    (stdOut, stdErr) = procObject.communicate(input=pInput)

    removeVars()  # clear variables

    if len(stdErr) == 0:  # subprocess finished execution without any errors
        serverResponse = "HTTP/1.1 200 OK\n"
        serverResponse += stdOut
    else:  # error occurred while running the script
        print(stdErr)
        serverResponse = "HTTP/1.1 500 Internal Server Error\n"
        serverResponse += "Content-Type: text/plain\n\n"
        serverResponse += "Internal Server Error"
    return serverResponse


# parse the request and respond appropriately
def handleRequest(file):
    initLine = file.readline()
    headers = getHeaders(file)
    body = getBody(file, headers)
    print("\n" + initLine[:-1])

    if len(initLine.split()) != 3 or headers is None:
        # initLine isn't formatted properly
        response = "HTTP/1.1 400 Bad Request"
        response += "Content-Type: text/plain\n\n"
        response += "Invalid request syntax"
        file.write(response)
        return

    method, path, version = initLine.split()
    path = path[1:]  # remove the leading '/'
    parsedPath = path.split('?')[0]  # make only file path, parse out the query string
    print("Requested path ./{}".format(parsedPath))

    index = parsedPath.rfind('.')  # find last index of '.'
    extension = ""

    if index != -1 and index < len(parsedPath) - 1:  # requested resource is a file, and '.' is at a valid index
        extension = parsedPath[index + 1:]

    if extension == "py":
        if os.path.isfile(parsedPath):
            serverResponse = handleScript(path, headers, body, method)
        else:
            serverResponse = "HTTP/1.1 404 Not Found\n"
            serverResponse += "Content-Type: text/plain\n\n"
            serverResponse += "requested resource \"/{}\" not found".format(path)
    else:
        rFile = getFile(parsedPath)  # get the requested file
        serverResponse = generateResponse(rFile, method, parsedPath)

    file.write(serverResponse)


HOST = ''
PORT = 15093
ADDRESS = (HOST, PORT)

sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sSocket.bind(ADDRESS)
sSocket.listen(20)
print("Server started on port {}!".format(PORT))

while True:
    requestSocket, requestAddress = sSocket.accept()  # accept incoming request
    file = requestSocket.makefile('rw')  # create a file allowing reads and writes to the requestSocket
    handleRequest(file)  # process the request
    # clean up
    file.close()
    requestSocket.close()

sSocket.close()
