#!/bin/bash

echo "process withdraws"

echo -n "from_RRC_number: "
read from_RRC_number

chrlen=${#from_RRC_number}

if [ ${chrlen} == 1 ]; then
	from_RRC_number=0${from_RRC_number}
fi

echo -n "to_RRC_number: "
read to_RRC_number

chrlen=${#to_RRC_number}

if [ ${chrlen} == 1 ]; then
	to_RRC_number=0${to_RRC_number}
fi

echo "check: RRC_number  from RRC${from_RRC_number} to RRC${to_RRC_number}"
echo -n "Are You Sure (Y/N): "
read sure

if [ ${sure} != 'Y' ]; then
	exit 1
else
	echo "Continue..."
fi

python2.7 run_withdraw.py ${from_RRC_number} ${to_RRC_number}
