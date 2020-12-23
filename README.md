# Luxtronics2MQTT

This python script reads all operating values from an Luxtronics driven Heatpump (Alpha Innotec) and publish those values at an MQTT Broker.

The default publisher prefix is **home/heatpump/0**. The payload is an JSON Object like:

```json
{
  "Description" : "Abtauen seit (hh:mm:ss)",
  "Name" : "Time_AbtIn",
  "Field" : 141,
  "Value" : 595,
  "Details" : "0:09:55"
}
```

- **Name:** is the variable name</li>
- **Field:** is the index of the Data(One packet with ~200 4 Bytes Integer Values) returned by the Heatpump</li>
- **Value**: is the raw value returned</li>
- **Description**: is defined for each variable name in aValueDefinition</li>
- **Details**: further details if available(IP Address, Heatpumptype, OperatingState...)</li>

## Configuration

The default configuration values are provided in `heatpump2mqtt.confspec`. To override some or all of these values provide a `heatpump2mqtt.conf` file beneath the `heatpump2mqtt.py` script, e.g.:

```ini
[Heatpump]
host = 192.168.100.9

[MQTT]
host = 192.168.100.10
user = my-user
password = my-password
```

## Dependencies

Before running the script ensure that the required python modules are installed:

```bash
pip3 install -r requirements.pip.txt
```
