# Tart Assignment



## Environment

- run on localhost
- python 3.9.10
  - cannot use `ray` on python 3.8.2 environment




## Prerequisite

- Make a virtual environment

  ```shell
  $ cd tart_assignment
  $ python3 -m venv myvenv
  ```

- Run a virtual environment

  ```shell
  (myvenv) ~/tart_assignment $ source myvenv/bin/activate
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
(myvenv) ~/tart_assignment $ python manage.py migrate
```

```shell
(myvenv) ~/tart_assignment $ python manage.py runserver
```



## Multiprocessed vs Iterative

- Do web-crawling in 2 websites

  - Do web-crawling interatively &

  - Do web-crawling by multiprocessing using ray



- Code iterative

```python
def mk_result_iteratively(self):
  start = time.time()
  merged_info = []
  for platform in self.Platforms:
    merged_info.extend(self.get_info_directly(platform, status))
  end = time.time()
  print(f"{end - start:.5f} sec", "!!!!!!!!!!!!!!!!!!!")

  return merged_info
```



- Code Multiprocessing

```python
def mk_result_using_multiprocessing(self):
  start = time.time()
  merged_info = []
  for platform in self.Platforms:
    merged_info.extend(ray.get(get_info_async.remote(ListView(), platform=platform, status=status)))
  end = time.time()
  print(f"μ€ν μκ° : {end - start:.5f} sec", "!!!!!!!!!!!!!!!!!!!")
  
  return merged_info
```



- **Expectation**
  - Expect a significant difference **in execution time**.

- **Result**

  ![multiprocessing vs iterative](./_imgs_for_doc/multiprocessingVSiterative.png)

  - There was **no significant difference..** π’
  - ~~Why? Something wrong..?~~



- **Troubleshooting**
  - **λ¬Έμ  μμΈ**

    - `ray.get()`μ μ°μμ μΌλ‘ forλ¬Έμ ν΅ν΄μ νΈμΆμ ν κ². 
    - μ΄λ κ² μ°μμ μΌλ‘ `ray.get()`μ νΈμΆνκ² λλ©΄, **λμ€μ νΈμΆλ `ray.get()`μ μμ νΈμΆλ `ray.get()`μ μμμ΄ λλ λ κΉμ§ κΈ°λ€λ¦¬λ λ¬Έμ κ° μκ²¨λ²λ¦Ό**
    - μ¦, λ³λ ¬μ²λ¦¬κ° μλλ κ².

  - **ν΄κ²°**

    - `[FUNCTION].remote()`λ₯Ό μμ°¨μ μΌλ‘ **μ¬λ¬ λ²** νΈμΆ 
    - `ray.get()`μ λ§μ§λ§μ **ν λ²λ§** νΈμΆ

  - **Changed Code**

    ```python
    def mk_result_using_multiprocessing(self):
    	start = time.time()
    	merged_info = [
    			get_info_async.remote(ListView(), platform=platform, status=status) for platform in self.Platforms
        ]
    	objs = ray.get(merged_info)
    	end = time.time()
    	print(f"{end - start:.5f} sec", "!!!!!!!!!!!!!!!!!!!")
    
    	return sum(objs, [])
    ```

    

- **New Result**

  - **Iterative Result**

    ![multiprocessing vs iterative](./_imgs_for_doc/res_iter.png)

  - **Multiprocessing Result**

    ![multiprocessing vs iterative](./_imgs_for_doc/res_multi.png)

  - **Chart**

    ![multiprocessing vs iterative](./_imgs_for_doc/multiprocessingVSiterative2.png)

    - There was **the significant difference!** π

  
