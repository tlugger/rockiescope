Rockiscope ♋️
============
✨It's not very good✨

Install
-------
Using virtalenv is preferred since that's what I prefer to use.
You'll need your Twitter credentials exported to your environment as:
```
CONSUMER_KEY (shown as API Key on Twitter?)
CONSUMER_SECRET (shown as API Key Secret on Twitter?)
ACCESS_TOKEN
ACCESS_TOKEN_SECRET
```

create a virtual environemnt:
```
virtualenv venv
source venv/bin/activate
```
install requirements
```
pip install -r requirements.txt
```

Run
---
```
python main.py
```

run as daemon service (may need to update paths in rockiscope.service)
```
sudo mv rockiscope.service /etc/systemd/system/.
sudo systemctl daemon-reload
sudo systemctl enable rockiscope.service
sudo systemctl start rockiscope.service
```

Contributing
------------
Why?