# python-influxdb-ups-monitor

A simple Python script that allows for you to monitor your PowerWalker UPS (connected via serial) by returning various parameters that are fed into InfluxDB (Telegraf).

## Installation

```bash
git clone https://github.com/CreepPork/python-influxdb-ups-monitor
pip3 install -r requirements.txt
```

## Usage

1. Edit the `ups-monitor.py` file to add your own services to monitor via ping
2. Configure your `telegraf.conf` (see example [here](#example-telegraf-configuration))
3. It will create a metric called `upses`, use this in your Grafana dashboard
4. Ready!

### Example Telegraf configuration

```conf
[[inputs.exec]]
  commands = [
    '/usr/bin/python3 /etc/telegraf/inputs/ups-monitor.py'
  ]
  interval="30s"
  timeout="30s"
  data_format="influx"
```

## Security

If you discover any security related issues, please e-mail [security@garkaklis.com](mailto:security@garkaklis.com) instead of using the issue tracker.

## Credits

- [Ralfs Garkaklis](https://github.com/CreepPork)
- [Thomas Jensen](https://github.com/thomasjsn)
- [All Contributors](https://github.com/CreepPork/python-influxdb-ups-monitor/contributors)

## License

The MIT License (MIT). Please see [License File](LICENSE.md) for more information.
