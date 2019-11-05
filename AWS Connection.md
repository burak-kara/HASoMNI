# How to connect AWS ec2 instance

## WinSCP or Cyberduck - SFTP protocol
### Server machine
- DNS: ec2-34-204-87-0.compute-1.amazonaws.com
- Public IP: 34.204.87.0
- Private DNS: 172.31.39.41
- key is publiched via whatsapp
### Gateway machine
- DNS: ec2-54-91-200-127.compute-1.amazonaws.com
- Public IP: 54.91.200.127
- Private DNS: 172.31.84.69
- key is publiched via whatsapp

## Gitbash
ssh -i "key.pem" ec2-user@DNS


