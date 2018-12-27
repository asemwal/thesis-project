#!/bin/bash

echo "Connection to mars-cys.ewi.tudelft.nl"
echo -n "Username: "
read username

ssh ${username}@mars-cys.ewi.tudelft.nl
