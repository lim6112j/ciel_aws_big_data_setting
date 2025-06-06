# aws DataLake/InfluxDB

0. bitnami application credential in .env

1. edit ~/.ssh/config

```
Host ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com
		 IdentityFile /Users/byeongcheollim/.ssh/ciel_big_data_ed25519.pem
```
2. run cmd on terminal

```

ssh -i "ciel_big_data_ed25519.pem" bitnami@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com

or

ssh bitnami@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com
```

3. emacs setting

C-c t
C-c C-w e

add below

```
** aws influxdb
 - path :: /ssh:bitnami@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com:/home/bitnami

```
# ciel_aws_big_data_setting
# ciel_aws_big_data_setting
