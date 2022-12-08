if [[ "$(service lightdm status | grep Active | awk -F ' ' '{print $2}')" == "active" ]]; then
    sudo chvt 1
    sudo service lightdm stop
else
    sudo service lightdm start
fi
