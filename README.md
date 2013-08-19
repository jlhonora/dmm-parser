## RS232 parser for Mastech MS8226 and MS8226T Multimeters ##

This script implements a parser for the Mastech MS8226(T) series Digital Multimeters. To use the script, simply connect the RS232 optical cable to your PC and run:

```
	./mastech.py
```

Currently supported for Linux and Mac OS X. To use in Windows, simply change the serial port name to whatever COM you are using.

### Dependencies ###

To run, please install the python libraries `serial` and `bitarray` (try with `pip install serial bitarray`).

### Documentation ###

I based this work on the documents available in the `doc` folder.
