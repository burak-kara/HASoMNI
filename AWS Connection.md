# How to connect AWS ec2 instance

### Server machine
- DNS: ec2-3-134-95-115.us-east-2.compute.amazonaws.com
- Public IP: 3.134.95.115
- Private IP: 172.31.39.64
- key is published via whatsapp

### How to Connect WinSCP or Cyberduck - SFTP protocol
- Address: DNS
- Username: ec2-user
- Password: -leave blank-
- Quite Similar Steps: https://winscp.net/eng/docs/guide_amazon_ec2

## Gitbash or any other terminal supports bash/ssh
- ssh -i "seniorSenior.pem" ec2-user@DNS
- Quite Similar Steps: https://protechgurus.com/connect-ec2-linux-instance-using-putty-gitbash-web-browser/

- ![Connect](https://github.com/burakkkara/SeniorProject/blob/master/images/connect.png)


## How to Run Server.py in Server Machine
- cd server
- python3.7 Server.py

- ![Run](https://github.com/burakkkara/SeniorProject/blob/master/images/run.png)
## Possible Mistakes
- Do not change the IP's of server and gateway at the beginnig of each file
