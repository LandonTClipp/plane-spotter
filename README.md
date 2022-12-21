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
4. Ensure that you have chromum installed in your environment

Note: you can specify alternate config paths by setting the `PLANE_SPOTTER_CONFIG_PATH` environment variable, or by specifying the value on the command line using `--config-path`.

Backends
=========

This package allows for different backends to be specified for the ADS-B data and notifications. By default, we use ADSBExchange and Twitter for these backends, respectively. As new backend implementations are created, you can explicitly specify which one you want on the command line like:

```
python3 -m plane_spotter.scripts.notify +adsb_backend=adsbexchange +notification_backend=twitter
```

Or by modifying the default values in your `notify.yaml` config file.

Notification Backends
-----------------------

|name|description|
|---|----------|
| __twitter_selenium__ | This backend uses selenium to open a chromium web browser. This is the default choice as using the official Twitter v2 API requires an Elevated Access service account, which are available only under explicit approval from Twitter. Selenium uses the Twitter front-end which only requires a simple user account. This can even be used on your personal account! |
| __twitter_api__ | This backend has not been created yet. This will use the v2 Twitter REST API |


ADS-B Backends
-----------------
|name|description|
|---|----------|
| __adsb_exchange__ | This uses the RapidAPI backed for ADS-B Exchange: https://rapidapi.com/adsbx/api/adsbexchange-com1 This is the best API available for ADS-B data as it's incredibly simple to use and is well-maintained. This is the default choice. Access to the API requires a $10/month subscription. |



Example Run
==============

```
(ve) [ltclipp@landon-virtualbox plane-spotter]$ python3 -m plane_spotter.scripts.notify 
2022-12-19 14:15:04 [info     ] starting                       adsb_backend=adsbexchange notification_backend=twitter
2022-12-19 14:15:04 [info     ] instantiating ADS-B backend    adsb_backend=adsbexchange notification_backend=twitter
2022-12-19 14:15:04 [info     ] instantiating notification backend adsb_backend=adsbexchange notification_backend=twitter
2022-12-19 14:15:04 [info     ] Plane last known location      adsb_backend=adsbexchange lat=55.997177 lon=-60.443698 notification_backend=twitter
2022-12-19 14:15:05 [info     ] Nearest airport info:          adsb_backend=adsbexchange notification_backend=twitter
2022-12-19 14:15:05 [info     ] 
{
    "ident": "CNH2",
    "type": "small_airport",
    "name": "Natuashish Airport",
    "elevation_ft": "30",
    "continent": "NA",
    "iso_country": "CA",
    "iso_region": "CA-NL",
    "municipality": "Natuashish",
    "gps_code": "CNH2",
    "iata_code": "YNP",
    "local_code": "CNH2",
    "coordinates": [
        55.913898,
        -61.184399
    ],
    "distance_to_coordinates": 47.029824474752026
}
 adsb_backend=adsbexchange notification_backend=twitter
```

