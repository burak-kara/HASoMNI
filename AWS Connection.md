# How to connect AWS ec2 instance

## WinSCP or Cyberduck - SFTP protocol
### Server machine
- DNS: ec2-3-134-95-115.us-east-2.compute.amazonaws.com
- Public IP: 3.134.95.115
- Private IP: 172.31.39.64
- key is published via whatsapp
### Gateway machine
- DNS: ec2-54-91-200-127.compute-1.amazonaws.com
- Public IP: 54.91.200.127
- Private IP: 172.31.84.69
- key is published via whatsapp

### How to Connect
- Address: DNS
- Username: ec2-user
- Password: -leave blank-
- Quite Similar Steps: https://winscp.net/eng/docs/guide_amazon_ec2

## Gitbash
- ssh -i "seniorSenior.pem" ec2-user@DNS
- Quite Similar Steps: https://protechgurus.com/connect-ec2-linux-instance-using-putty-gitbash-web-browser/

## How to Run Server.py in Server Machine
- cd server
- python3.7 Server.py

## Possible Mistakes
- Do not change the IP's of server and gateway at the beginning of each file
