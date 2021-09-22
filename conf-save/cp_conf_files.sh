cp /etc/fstab fstab
crontab -l > crontab
cp /etc/systemd/system/sjwebui.service .
cp /shares/USBDRIVE/SYNCJOBS.conf/etc/* ./etc
# Save samba conf too
cp /etc/samba/smb.conf ./smb
