# Documentation


## Ubuntu server deploying
Clone the repository to your VM/server and get to the repository
```bash
git clone -name-
cd -name-
```

Then create a virtual python environment
```bash
apt install python3
apt update
python3 -m venv .venv
```

Install all hoocks
```bash
pip install requirements.txt
```

Then you need to create a mariadb server.
```bash
apt install mariadb-server
```


Enter mariadb
```bash
mariadb -p
```
```bash
SHOW GLOBAL VARIABLES LIKE 'PORT';
```

```bash
SHOW GLOBAL VARIABLES LIKE 'HOSTNAME';
```

Then enter password
```sql
CREATE DATABASE db;
USE db;
```

```sql
CREATE TABLE users(username VARCHAR(64), team_name TEXT, team_members TEXT, stations TEXT, current_station TEXT, team_size INT, id INT);
```