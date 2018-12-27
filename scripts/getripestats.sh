
# 	Get RIPE Collecter Peer Stats
#
#
#
a=1
while [ $a -lt 10 ]
do
tot=`GET http://www.ris.ripe.net/peerlist/rrc0$a.shtml| grep "Total peerings:"|cut -d: -f2|cut -d\< -f1`
v4=`GET http://www.ris.ripe.net/peerlist/rrc0$a.shtml| grep "IPv4 full tables:"|cut -d: -f2|cut -d\< -f1`
v6=`GET http://www.ris.ripe.net/peerlist/rrc0$a.shtml| grep "IPv6 full tables:"|cut -d: -f2|cut -d\< -f1`
echo "rrc0$a|$tot|$v4|$v6"
a=$((a+1))
done
while [ $a -lt 24 ]
do
tot=`GET http://www.ris.ripe.net/peerlist/rrc$a.shtml| grep "Total peerings:"|cut -d: -f2|cut -d\< -f1`
v4=`GET http://www.ris.ripe.net/peerlist/rrc$a.shtml| grep "IPv4 full tables:"|cut -d: -f2|cut -d\< -f1`
v6=`GET http://www.ris.ripe.net/peerlist/rrc$a.shtml| grep "IPv6 full tables:"|cut -d: -f2|cut -d\< -f1`
echo "rrc$a|$tot|$v4|$v6"
a=$((a+1))
done
