cp /etc/fstab fstab
crontab -l > crontab
cp /etc/systemd/system/sjwebui.service .
cp /shares/USBDRIVE/SYNCJOBS.conf/etc/* ./etc
