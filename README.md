# plane-spotter

Installation
--------------

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

Setup
------

1. Rename the `config/` directory to `production_config/`. This is done so that the scaffolding provided in `config/` doesn't
get committed to git and expose your secrets.
2. Populate the `production_config/` files with your secret API keys as necessary.
3. Then, source `env.sh` to initilize your environment

Note: you can specify alternate config paths by setting the `PLANE_SPOTTER_CONFIG_PATH` environment variable, or by specifying the value on the command line using `--config-path`.


Example Run
------------

```
(ve) [ltclipp@landon-virtualbox plane-spotter]$ python3 -m plane_spotter.scripts.notify+adsb_backend=adsbexchange +notification_backend=twitter
2022-12-16 22:11:55 [info     ] starting                       adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] instantiating ADS-B backend    adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] instantiating notification backend adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] Elon plane last known location adsb_backend=adsbexchange lat=37.359311 lon=-121.93036 notification_backend=twitter
```

