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

Example Config
---------------
The configuration file must be named `notify.yaml`. You can specify an alternate directory through `--config-path`. `--config-path` must be the directory where the yaml file lives, not the path of the file itself.

```yaml
adsb_backend:
  api_hostname: "adsbexchange-com1.p.rapidapi.com"
  api_key: "foobar"
notification_backend:
  key_id: foo
  key_secret: bar
```

Example Run
------------

```
(ve) [ltclipp@landon-virtualbox plane-spotter]$ python3 -m plane_spotter.scripts.notify --config-path ~/git/LandonTClipp/plane-spotter/ +adsb_backend=adsbexchange +notification_backend=twitter
2022-12-16 22:11:55 [info     ] starting                       adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] instantiating ADS-B backend    adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] instantiating notification backend adsb_backend=adsbexchange notification_backend=twitter
2022-12-16 22:11:55 [info     ] Elon plane last known location adsb_backend=adsbexchange lat=37.359311 lon=-121.93036 notification_backend=twitter
```

