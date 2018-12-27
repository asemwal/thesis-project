#!/bin/bash

echo ""
echo '/-------------------------------------\'
echo "|Starting Command-Line-Interface (CLI)|"
echo "\-------------------------------------/"
echo ""

echo "If you want to capture std_out to a file in ../output/"
echo "Enter a file name. Otherwise, leave empy."
echo -n "File Name: "
read file_name

if [ "${file_name}" != '' ]; then
	echo ""
	echo "Using ../output/"$file_name".output"
	echo "Use capture.sh to see captured std_out"
	echo "printer_id = $file_name"
	echo ""
	python2.7 run_CLI.py $file_name
else
	echo ""
	echo "Not capturing output"
	echo ""
	python2.7 run_CLI.py
fi


