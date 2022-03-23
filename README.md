# TartProject



## Environment

- run on localhost



## Prerequisite

- Make a virtual environment

  ```shell
  $ cd tart_project
  $ python3 -m venv myvenv
  ```

- Run a virtual environment

  ```shell
  (myvenv) ~/tart_project $ source myvenv/bin/activate
  ```

- Install requirements

  - install requirements

    ```shell
    (myvenv) ~$ pip install -r requirements.txt
    ```

  - pip upgrade

    ```shell
    (myvenv) ~$ python3 -m pip install --upgrade pip
    ```

    

## Usage

```shell
(myvenv) ~/tart_project $ python manage.py makemigrations
(myvenv) ~/tart_project $ python manage.py migrate
```

```shell
(myvenv) ~/wolley-deploy$ python manage.py runserver
```


