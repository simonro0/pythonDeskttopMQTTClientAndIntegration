# Python Desktop MQTT Client And Windows Integration

This python script allows to integrate a windows 10 PC to mqtt smart home and be also be partially controlled.

__MQTT Capabilities:__
- Publish some information about the computer
    - running State via "computer/running"
    - start time via "computer/starttime"
    - shutdown time via "computer/shutdowntime"
    - last will via "computer/lastwill"
- receive notifications via "computer/command/hint topic"
- start shutdown timer via "computer/command/shutdown topic"
- change the sound volume of a windows computer via "computer/command/<subcommand>"
  - usable subcommands are "volume_up", "volume_down" and "volume_set" and the last needs the volume in % as payload

__Current TODO's:__
- extract config file (IP, Port, user, password, etc...)
- integrate security
- integrate with other scripts on computer
- encapsulate some functionality to be much better readable
- add some tests
- SSO integration if possible?
- Combine multiple topics to just one with more data
- Integrate Flo's image recognition to analyse local images from onedrive
  - recognize images of gascounter, enegy meter and person scale so those can be converted to actual savable values
- and much more...