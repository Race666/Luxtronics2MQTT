# Luxtronics2MQTT

This python script reads all operating values from an Luxtronics driven Heatpump (Alpha Innotec) and publish those values at an MQTT Broker.

The publisher prefix (default  	**home/heatpump/0** )  could defined at the top script. The payload is an JSON Object like:
```
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

## Dependencies

Before running the script ensure that the required python modules are installed:

```bash
pip3 install -r requirements.pip.txt
```
