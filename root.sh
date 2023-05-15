# add required files into root (This is for developer)
# Author: Taha Canturk
# Github: Kibnakamoto
# Date: Apr 16, 2023
VAR=/home/kibnakamoto/workspace
if [ ${PWD} = "$VAR/usb-app" ]; then
	cd pico-ducky/
	git pull
	cp boot.py duckyinpython.py code.py webapp.py wsgiserver.py ../add_to_pico/root/ -f
	cp ../language.py ../add_to_pico/root -f
	echo "win|us" > ../add_to_pico/root/choices
else
	echo "in wrong folder, go to usb-app"
fi

