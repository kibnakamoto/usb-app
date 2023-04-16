# add required files into root (This is for developer)
if [path basename "$PWD" = "usb-app"]; then
	cd pico-ducky/
	git pull
	cp /boot.py duckyinpython.py code.py webapp.py wsgiserver.py ../add_to_pico/root/
else
	echo "in wrong folder, go to usb-app"
fi

