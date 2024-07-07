# world-of-picross-api

Back-end of world-of-picross web application

## Installation

### Requirements

Python 3.12 (make sure it's the default python executable).

### Installing the virtual environement

Open a Terminal at the project's root and execute

```bash
python -m venv .venv
```

### Activating the virtual environment

Open the Terminal located at the project's root and execute

```bash
.venv\Scripts\activate
```

### Installing the requirements

```bash
pip install -r requirements.txt
```

### Creating the database

1. Install psql

2. Open the postgres REPL and execute the followings (replace `.......` by an actual password) to create the database:

  ```sql
  CREATE ROLE picross WITH LOGIN PASSWORD '.......';
  CREATE DATABASE picross OWNER picross;
  ```

3. Open a Terminal at the root of the project and execute the followings to init and seed the database:

```bash
psql -U picross -d picross -f database/init.sql
psql -U picross -d picross -f database/seed.sql
```

## Running the server

Make sure you activated the python virtual environment and execute

```bash
fastapi dev main.py
```
