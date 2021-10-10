# Blowerdoor PDF parser
This small flask server parses PDFs and looks for blowerdoor relevant information and displays them in a Web-Interface.

![THS-Blowerdoor Rave Web-Interface](https://m.athq.de/pictures/blowerdoor-raven.png)

## System Example

    [Unit]
    Description=THS Blowerdoor Raven blowerdoor.ths.atlantishq.de
    After=network.target
    
    [Service]
    WorkingDirectory=/home/username/ths-blowerdoor-raven/
    Type=simple
    User=username
    ExecStart=/usr/bin/python3 ./server.py --interface 127.0.0.1 --port 5001
    MemoryHigh=2G
    CPUQuota=100%
    
    [Install]
    WantedBy=multi-user.target
