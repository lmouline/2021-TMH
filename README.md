PV Simulator  Challenge - TMH Code Assessment
---

This repository contains my implementation of the PhotoVoltaic (PV) simulator challenge. It contains two services:

- one that mocks a meter by sending random consumption values between 0 and 9000 W through a RabbiMQ broker,
- one that mocks a PV service by consuming one meter message, generating a random PV power value, adding the two, and writing the result in a file.

# Requirements

- A running [RabbitMQ](https://www.rabbitmq.com/) server
    - please refer to the [documentation](https://www.rabbitmq.com/download.html) to know how to install and run one
- [Python](https://www.python.org/) 3.8 or later
- [Pip](https://pypi.org/project/pip/) package installer
    - you can use any other package installer at your own risk

# How to run?

The repository contains two main scripts to launch the two services:

- `demo_meter.py` to run the meter service,
- `demo_pv_service.py` to run the PV service.

In two different terminals, you will have to execute these scripts. You can add the `-h` or `--help` option to get more information regarding the usage of these scripts.
Below, we detail a bit more the procedure.

## 1. Start your RabbitMQ instance

Before executing any script, you should run an instance of RabbitMQ as described in their [documentation](https://www.rabbitmq.com/download.html).

**Warning:** The current implementation do not support any credentials for the connection to the broker.
Please be sure that the script will be able to connect to the broker with only its IP address (or hostname) and the port.

When the instance is running without any error, you can report the configuration in a `.ini` file.
The configuration file should contain a `broker` section as follows:

````
[broker]
host = <HOST_NAME or IP>
port = <PORT>
````

If not provided, the default values are `localhost` for the host and 5672 for the port.

## 2. Install required packages

This implementation is based on ony one external library: [pika](https://pypi.org/project/pika/) v.1.1.0, one client implementation of the RabbitMQ broker.
You can install it manually or using the `requirements.txt` file: `pip install -r requirements.txt`.

*(If you give a look at the `requirements.txt` file, you will see another dependency. 
This dependency is only used in the test suite.)*

## 3. Execute the meter service

You can start the meter service by executing the `demo_meter.py` script.
It has three options:

- `-h` or `--help` to print the usage,
- `-conf` or `--configuration-file` to define the path of the broker configuration file. The default value is `broker.ini`,
- `-nb` or `--nb-meter` to define the number of meters to mock. Default value is 1. If the value is negative or 0, we silently choose the default value.

In the logs printed in the console, you will see the id of the meters created as follows (here for 3 meters):

`INFO:root:Meter created: ['Meter_0', 'Meter_1', 'Meter_2']`.

RabbitMQ is configured with the default exchange.
We use the meter ids as routing keys.
The PV service need to know the meter ids to start consuming the channel of the meter it is interested in.
The meter ids are on the form: `Meter_<COUNT>`, with count starting at 0 and being increased at every meter creation.

You can stop the service at anytime with `Ctrl-C`.

**Warning:** RabbitMQ channels are destroyed when the script ends. 
Do not stop it before executing the PV service, or the messages will not be consumed by the PV service.

## 4. Execute the PV service

You can start the PV service by executing the `demo_pv_service.py` script.
It has two options:

- `-h` or `--help` to print the usage,
- `-conf` or `--configuration-file` to define the path of the broker configuration file. The default value is `broker.ini`,
- `-ids` or `--meter-ids` to define the channel to consume. It expects a **space separated list** of IDs with at least one element.

The service will then instantiate any many PV services as meter ids: a PV service consume messages of exactly one meter.
A CSV file will then be created for each meter with the following name: `<METER_ID>-<YEAR>-<MONTH>-<DAY>.csv`.
If it already exists, the result of the PV service will be appended to the file. 
**Warning**: if the file already exists, we do not check if the CSV headers corresponds to the data we put.

The CSV file contains five columns:

- `meter_id`: the ID of the meter
- `time_s`: EPOCH in seconds, timestamps at which the meter has read its value
- `meter_power_value_w`: power value measured by the meter, in Watt
- `pv_power_value_kw`: power value of the PV service, in kilo-Watt
- `sum_meter_pv_w`: sum of the two power values in Watt

**Disclaimer**: we assume here that the measurement of the meter and PV service are perfectly synchronous. 
This is why the final timestamps is the one of the meter. This is, of course, a simplification of a real case.