# Student Backend

This repository is the MySQL implementation and Bottle API

## Requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
python 3.10
Docker
pip install bottle
pip install bottle-pymysql
pip install pymysql
```

## How to run

```bash
cd docker
docker-compose up -d
```
Enter "8080" port:
1) Create "Student" database
2) From SQL commands run gradeTable.sql and studentTable.sql

```bash
cd ..
python api.py
```
