# Queue Managment System

Created a queue managment system for intianting a call between a Agent and User

Components used
1. PostgresDB
2. Python

## Process
* Clone the repository from the master branch

* Get into the directory
* Run:
 `pip install -r requirements.txt`

## Running the script

### To run the script

command `python wsqi.py` 

The program creates a flask webserver in the localhost, which is restricted to use only for development for production it is highly recomended to run through a WSQI server like gunicorn.

command `gunicorn -b 0.0.0.0:PORT --workers worker wsgi:app`