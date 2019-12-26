apt-get update
apt-get install git -y

docker version > /dev/null || curl -fsSL get.docker.com | bash
service docker restart

cd /root
git clone https://github.com/cha0sCat/JavBus_Py

cd JavBus_Py
git checkout datastore

# docker pull python

docker build -t javbus .
docker run -itd --name javbus -e REDIS_URL=redis://user:RUtXSUag3PVZ@104.199.225.82:6379 javbus


#### v2
docker version > /dev/null || curl -fsSL get.docker.com | bash
service docker restart
docker run -itd --name javbus -e REDIS_URL=redis://user:RUtXSUag3PVZ@104.199.225.82:6379 --log-opt max-size=50m --log-opt max-file=3 cha0scat/javbus_py

## AZ CI
az container create --image cha0scat/javbus_py --resource-group javbus --location eastasia --name javbus5 --os-type Linux --cpu 2 --memory 1 --ip-address public --ports 80 --environment-variables REDIS_URL=redis://user:RUtXSUag3PVZ@104.199.225.82:6379 --verbose
