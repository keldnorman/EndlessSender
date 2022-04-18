# EndlessSender
Send infinite amount of data to clients asking for it 

```

# In the script you can specify the text file to read data from:
FILENAME         = "text.txt"    # Get text to send from this file
PATHNAME         = "."           # Find file with text here - Do not end with /

# and the IP and port to listen on:
LISTEN_ADDR      = "127.0.0.1"   # Listen on this IP address
LISTEN_PORT      = 1060          # Listen on this PORT

# Start the program by running :

./send_endless_data.py
```

![start](https://github.com/keldnorman/EndlessSender/blob/main/start.png?raw=true)

```
# Test the flow with netcat:

nc localhost 1060
```
![start](https://github.com/keldnorman/EndlessSender/blob/main/test.png?raw=true)

