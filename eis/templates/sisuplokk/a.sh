for a in `ls sisuplokk.*`
do
	b=`echo $a | sed 's/sisuplokk.//'`
	mv $a $b
done

