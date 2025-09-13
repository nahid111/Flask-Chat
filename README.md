# Flask Socket.io Chat App
Realtime Chat application built with Flask, Socket.io & MySQL

### installation
- clone the repo & cd into it
- create virtual env and install dependencies
    ```bash
    $ python3 -m venv .venv
    $ source ./.venv/bin/activate 
    $ pip install uv
    $ uv sync --frozen
    ```

### migration
- Create *.env* file using *.env.example*
- Create Database tables - 
    ```bash
    $ flask --app App/ db init
    $ flask --app App/ db migrate -m "Initial migration."
    $ flask --app App/ db upgrade
    ```

### run app
    ```bash
    $ python run.py
    ```
