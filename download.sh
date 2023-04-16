# This is a developer file for updating the required files from the cloud so that the hacking usb is up to date
# Author: Taha Canturk
# Github: Kibnakamoto
# Date: Apr 15, 2023

# reset the lib and root folder
rm -rf add_to_pico/lib add_to_pico/root
mkdir add_to_pico/lib add_to_pico/root

# download root
sh root.sh

# download lib
sh lib.sh
