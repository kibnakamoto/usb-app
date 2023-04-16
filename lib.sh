# This is a developer file for download lib folder content of the microcontroller

# download the circuit python
firefox https://downloads.circuitpython.org/bin/raspberry_pi_pico/en_US/adafruit-circuitpython-raspberry_pi_pico-en_US-8.0.5.uf2

# copy the required files into add_to_pico
cd adafruit-circuitpython-bundle-8.x-mpy-20230415/lib
cp adafruit_hid adafruit_debouncer.mpy adafruit_ticks.mpy ../../add_to_pico/lib
cp -r asyncio adafruit_wsgi ../../add_to_pico/lib

rm -rf ../ # adafruit-circuitpython-bundle-8.x-mpy-20230415/
