#!/bin/bash

if [ -d ~/powerplant_transmission ]; then
	echo "powerplant_transmission folder exists"
else
	echo "Creating powerplant_transmission folder"
	mkdir ~/powerplant_transmission
fi

if [ -p ~/powerplant_transmission/temp_and_humidity ]; then
	echo "Pipe exists: temp_and_humidity"
else
	echo "Creating missing named pipe: temp_and_humidity"
	mkfifo ~/powerplant_transmission/temp_and_humidity
fi
