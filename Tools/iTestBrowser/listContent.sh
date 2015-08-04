#!/bin/bash

echo
export DEST=itest_actions

for fname in $(find itest_actions -name '*.txt'); do
    echo "INPUT: " $fname
    folder=`echo $fname | cut -d "/" -f 2`
    filename=`echo $fname | rev | cut -d "/" -f 1 | rev`
    newfile=`echo $filename | rev | cut -d "." -f 2- | rev`

    destPath=$DEST/$folder  	
  	file_name=`echo $fname | cut -c 2-`
  	destFile=''
    type_check=`echo $destPath | grep "\."`
	
	if [ $type_check ]; then
	  	destFile="itest_actions/$newfile.html"
	else
	  	destFile="$destPath/$newfile.html"
	fi

	echo "<html><body bgcolor=#a0a0a0><p span style='font-size:13pt; font-family: Arial; font-weight:bold; text-align:center'>$newfile</p>" > $destFile
	echo "<p span style='font-size:11pt; font-family: Calibri; margin-left:20px'>" >> $destFile
	
	cat $fname | while read line
	do
		is_LC=`echo $line | grep "^[a-z].*"`
		if [ $is_LC ]; then
			echo "$line<br>" >> $destFile
		else
			echo "<a href='../itest_params/$line.html' target='frame3'>$line</a><br>"  >> $destFile
		fi

	done
	
	echo "</p><br></body></html>" >> $destFile

	echo

done
