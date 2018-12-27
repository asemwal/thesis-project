#!/bin/bash

echo "Connecting and Tunneling to mars-cys.ewi.tudelft.nl"
echo -n "Username: "
read username

ssh -L 9200:eris:9200 -L 5601:10.0.0.1:5601 -L 4000:localhost:4000 ${username}@mars-cys.ewi.tudelft.nl
