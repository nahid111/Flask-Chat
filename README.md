# Flask_Socket.io_Chat_App
Realtime Chat application built with Flask, Socket.io & MySQL

### installation
- install pipenv
```bash
$ sudo -H pip install -U pipenv
```
- clone the repo & cd into it
- install dependencies
```bash
$ pipenv install
```
- Create *config.py* inside *Config* directory using the *example_config.py*
- Create Database tables - 
```bash
$ pipenv run python migrations.py db init
$ pipenv run python migrations.py db migrate
$ pipenv run python migrations.py db upgrade
```
- run the app
```bash
$ pipenv run python run.py
```
