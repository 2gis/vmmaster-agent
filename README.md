vmmaster-agent
==============

Dependencies
-------------
Common:
 - python 2.7
 - pip

For Windows:
 - [pywin32](http://sourceforge.net/projects/pywin32/files/pywin32/)


Installation.
-------------------

Linux
-------

- Download and install deps for your OS.
- If you have installed git then run command in terminal:
```bash
sudo -E pip install -U git+https://github.com/2gis/vmmaster-agent.git#egg=vmmaster_agent
```
- Else download zip archive with repository from this page and extract. Run command:
```
python setup.py install
```

Windows 7/8/10
-----------------------------

- Download zip archive with repository from this page and extract.
- Open cmd and run command:
  ```
  C:/Python27/python.exe setup.py install
  ```
- Run vmmaster-agent.exe from C:/Python27/Scripts/

