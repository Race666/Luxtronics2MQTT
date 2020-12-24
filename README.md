# Luxtronics2MQTT

This python script reads all operating values from an Luxtronics driven Heatpump (Alpha Innotec) and publish those values at an MQTT Broker.

The default publisher prefix is **home/heatpump/0**. The payload is an JSON Object (see below).

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

### Payload content

The following data is published for each value:

- **Name:** is the Luxtronic variable name
- **Field:** is the index of the Data (one packet with ~200 4 Bytes Integer Values) returned by the Heatpump
- **Value**: is the raw value returned
- **Description**: is defined for each variable name in aValueDefinition
- **Details**: further details if available (IP Address, Heatpumptype, OperatingState...)

Option **one_value_per_message** publishes one MQTT message per operating value (default). This produces 200 small MQTT messages per cycle.

```ini
...
[MQTT]
message_type = one_value_per_message
...
```

Sample payload:

```json
{
  "Description" : "Abtauen seit (hh:mm:ss)",
  "Name" : "Time_AbtIn",
  "Field" : 141,
  "Value" : 595,
  "Details" : "0:09:55"
}
```

Option **all_values_in_one_message** publishes one MQTT message with all operating values.

```ini
...
[MQTT]
message_type = all_values_in_one_message
...
```

Sample payload (partial):

```json
{
  ...
  "Time_AbtIn": 595,
  "Time_AbtIn_Field": 141,
  "Time_AbtIn_Description": "Abtauen seit (hh:mm:ss)",
  "Time_AbtIn_Details": "0:09:55",

  "Temperatur_RFV2": 0.0,
  "Temperatur_RFV2_Field": 142,
  "Temperatur_RFV2_Description": "Raumtemperatur Raumstation 2 (\u00b0C)",
  "Temperatur_RFV2_Details": ""
  ...
}
```

## Dependencies

Before running the script ensure that the required python modules are installed:

```bash
pip3 install -r requirements.pip.txt
```
