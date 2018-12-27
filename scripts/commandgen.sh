if [ $# != "4" ];then echo "usage\ncommandgen.sh stage command year pattern"; exit 255;  fi
stg=$1
path="/home/asemwal/raw_data/$3/$4*"
if [ $stg != "1" ];then path="/home/asemwal/raw_data/$3/proc/$4*" ;   fi
bin="/home/asemwal/raw_data/scripts/stg$1/$2"
for file in $path
do
echo "python $bin $file "
done
