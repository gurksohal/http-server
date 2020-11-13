#!\venv\Scripts\python
import sys
from os import environ


# print the activation form
def activation_page():
    print("Content-type: text/html")
    print("")
    print('<html>')
    print('<form action="test.py" method="post">')
    print('<label for="name">Name:</label>')
    print('<input type="text" name="name">')
    print('<label for="name">Postal Code:</label>')
    print('<input type="text" name="postalcode">')
    print('<input type="submit" value="Locate">')
    print('</form>')
    print('</html>')


# print the welcome page, and set the cookie
def welcome_page(name, postalcode):
    # passed postal code is in the format R3T+2N2
    # replace + with a space
    postalcode = postalcode.replace("+", " ")
    display = name + " : " + postalcode
    print("Set-Cookie: " + name + " = " + postalcode)
    print("Content-type: text/html")
    print("")
    print('<html>')
    print('<h1>welcome</h1>')
    print('<h1>' + display + '</h1>')
    print('<form action="/test.py" method="post">')
    print('<input type="submit" value="Anonimize">')
    print('</form>')
    print('</html>')


# print error page
def error_page(postalcode):
    # format the + with a space, if it exists
    postalcode = postalcode.replace("+", " ")
    print("Content-type: text/html")
    print("")
    print('<html>')
    print('<h1>Error!</h1>')
    print('<h1>' + postalcode + ' is an invalid postal code. </h1>')
    print('<form action="/test.py" method="get">')
    print('<input type="submit" value="retry">')
    print('</form>')
    print('</html>')


# clear cookie and redirect to activation page
def redirect(name, postalcode):
    # clear cookie by setting a new one with the same name to have an expiry date in the past
    print("Set-Cookie: " + name + " = " + postalcode + "; Expires = Wed, 01 Jan 2020 00:00:00 GMT")
    print("Content-type: text/html")
    print("")
    print('<html>')
    print('<head>')
    print('<META HTTP-EQUIV="REFRESH" CONTENT=0;URL=http://localhost:15093/test.py>')
    print('</head>')
    print('</html>')


# get all form data
def get_form_date():
    querytext = sys.stdin.readlines()
    fields = {}
    for pair in querytext[0].split('&'):
        (key, value) = pair.split('=')
        fields[key] = value
    return fields


def validate_postal(postal_code):
    if len(postal_code) == 7 and postal_code[3] == '+':
        # group all the expected spots for letters and numbers in to two different variables
        numbers = postal_code[1] + postal_code[4] + postal_code[6]
        letters = postal_code[0] + postal_code[2] + postal_code[5]
        # check each only contains the right type
        return numbers.isdigit() and letters.isalpha()
    return False


if 'REQUEST_METHOD' in environ:
    # if cookie is passed along side the the request
    if 'HTTP_COOKIE' in environ:
        # get data from cookie
        (name, postalCode) = environ['HTTP_COOKIE'].split('=')
        if environ['REQUEST_METHOD'] == "GET":
            # show welcome page populated with data from the cookie
            welcome_page(name, postalCode)
        elif environ['REQUEST_METHOD'] == "POST":
            # redirect to welcome
            redirect(name, postalCode)
    else:  # no cookie passed
        if environ['REQUEST_METHOD'] == "GET":
            activation_page()
        elif environ['REQUEST_METHOD'] == "POST":
            # get form data
            data = get_form_date()
            if 'postalcode' in data:
                # if valid postal code was entered, show welcome page
                if validate_postal(data['postalcode']):
                    welcome_page(data['name'], data['postalcode'])
                else:
                    error_page(data['postalcode'])

