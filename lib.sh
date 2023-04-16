# This is a developer file for download lib folder content of the microcontroller

# make sure the path is already usb-app. This will make sure commands won't run accidents
if [path basename "$PWD" = "usb-app"]; then

	# download the circuit python
	firefox https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-8.0.5.uf2
	
	# move raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-8.0.5.uf2 to add_to_pico/uf2.uf2
	mv ~/Downloads/adafruit-circuitpython-raspberry_pi_pico-en_US-8.0.5.uf2 add_to_pico/uf2.uf2
	
	# download the circuitpython folder
	firefox https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20230415/adafruit-circuitpython-bundle-8.x-mpy-20230415.zip
	unzip ~/Downloads/adafruit-circuitpython-bundle-8.x-mpy-20230415.zip
	
	mv ~/Downloads/adafruit-circuitpython-bundle-8.x-mpy-20230415/ .

	# copy the required files into add_to_pico
	cd adafruit-circuitpython-bundle-8.x-mpy-20230415/lib
	cp adafruit_hid adafruit_debouncer.mpy adafruit_ticks.mpy ../../add_to_pico/lib
	cp -r asyncio adafruit_wsgi ../../add_to_pico/lib
	
	# if cd command didn't fail, then delete, otherwise, this is really dangerous to execute
	if [path basename "$PWD" = "lib"]; then
		rm -rf ../ # adafruit-circuitpython-bundle-8.x-mpy-20230415/
	else
		echo "Wrong path, make sure current folder is adafruit-circuitpython-bundle-8.x-mpy-20230415/lib"
	fi
else
	echo "Wrong path, make sure current folder is usb-app"
fi
