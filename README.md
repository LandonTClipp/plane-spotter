# plane-spotter

Installation
=============

```bash
[ltclipp@landon-virtualbox plane-spotter]$ python3 --version
Python 3.10.8
[ltclipp@landon-virtualbox plane-spotter]$ python3 -m venv ve
[ltclipp@landon-virtualbox plane-spotter]$ source ve/bin/activate
(ve) [ltclipp@landon-virtualbox plane-spotter]$ pip install -U pip
Requirement already satisfied: pip in ./ve/lib/python3.10/site-packages (22.2.2)
Collecting pip
  Using cached pip-22.3.1-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 22.2.2
    Uninstalling pip-22.2.2:
      Successfully uninstalled pip-22.2.2
Successfully installed pip-22.3.1
(ve) [ltclipp@landon-virtualbox plane-spotter]$ pip install -Ue .[dev]
```
