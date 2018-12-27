sum=0;
for file in `ls aspath_a*`;
do
echo $file; 
for line in `cat $file`;
do 
a=`echo $line| cut -d"|" -f2`;
sum=$((a+sum));
done;
echo "$file|$sum";
done
