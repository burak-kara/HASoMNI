# How to connect AWS ec2 instance

## WinSCP or Cyberduck - SFTP protocol
### Server machine
- DNS: ec2-34-204-87-0.compute-1.amazonaws.com
- Public IP: 34.204.87.0
- Private IP: 172.31.39.41
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
- ssh -i "key.pem" ec2-user@DNS
- Quite Similar Steps: https://protechgurus.com/connect-ec2-linux-instance-using-putty-gitbash-web-browser/


