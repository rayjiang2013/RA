#!/bin/bash

IFS=''

echo
fname="/Users/rcollazo/Downloads/RestAPITest/testcaselib.fftccat"
destFile=''

cat $fname | while read line
do
#	echo
#	echo "$line"
 	isCommand=`echo $line | grep "^[A-Z].*"`
 	if [ $isCommand ]; then
 		echo ">>> COMMAND: [$line]"
 		targetURL="https://github.com/mudynamics/avalanche_app/wiki/Avalanche-apis"

 		destFile="new_itest_actions/itest_params/$line.html"
# 		destFile="itest_actions/itest_params/$line.html"

 		echo "<html><head><script language=JavaScript>" > $destFile

 		echo "<!-- " >> $destFile
 		echo "function newWin(targetURL) { window.open(targetURL, '_blank', 'scrollbars=1, resizable=1, width=1100, height=800'); } " >> $destFile
 		echo " //--> " >> $destFile

 		echo "</script></head><body bgcolor=#808080><center><p span style='font-size:13pt; font-family: Arial; font-weight:bold'>$line</p>" >> $destFile

 		echo "<p span style='font-size:8pt; font-family: Calibri; margin-left:5px; margin-right:5px'>" >> $destFile
 		echo "<table border=1 bgcolor=#ececec cellspacing=0 cellpadding=4 width=95% style='font-size:8pt; font-family: Calibri; font-weight:normal'>" >> $destFile
 		echo "<tr style='background-color:#acacac; font-weight:bold; text-align:center'><td>VARIABLE NAME(s)</td><td>DESCRITPTION</td><td>DEFAULT VALUE</td><td>MANDATORY</td></tr>" >> $destFile

 		continue
 	fi
 	
 	nRows=1


 	isVar=`echo $line | egrep "[A-z].+"`
 	if [ $isVar ]; then
 		
 		thisVar='&nbsp;'
 		theDescription='&nbsp;'
 		theDefaults='&nbsp;'
 		isMandatory='&nbsp;'
 		
 		var=`echo $line | sed -E 's/([A-z0-9.+]) .*/\1/'`
 		thisVar=`echo $var | sed 's/^[ ]*//'`

 		thisDesc=`echo $line | grep "\[DESCRIPTION\: "`
		if [ $thisDesc ]; then
	 		var=`echo $line | sed -E 's/.*\[DESCRIPTION\: (.*)/\1/'`
	 		theDescription=`echo $var | cut -d ']' -f 1`
			nRows=`echo $theDescription | awk 'BEGIN {FS=","} ; {print NF}'`
		fi

 		thisDef=`echo $line | grep "\[DEFAULT_VALUE\: "`
		if [ $thisDef ]; then
	 		var=`echo $line | sed -E 's/.*\[DEFAULT_VALUE\: (.*)/\1/'`
	 		theDefaults=`echo $var | cut -d ']' -f 1`
		fi

 		isMand=`echo $line | grep "\[MANDATORY\]"`
		if [ $isMand ]; then
			isMandatory="TRUE"
		fi
 		
 		echo "<tr>  <td rowspan=$nRows style='background-color:#cccccc; font-weight:bold'><p>$thisVar</p></td>" >> $destFile
		echo $theDescription | awk 'BEGIN {FS=","} ; {for(i=1;i<=1;i++){print "<td><p>" $i "</p></td>"}}' >> $destFile
 		echo "<td rowspan=$nRows><p>$theDefaults</p></td>" >> $destFile
 		echo "<td rowspan=$nRows style='text-align:center'><p>$isMandatory</p></td>  </tr>" >> $destFile

		echo $theDescription | awk 'BEGIN {FS=","} ; {for(i=2;i<=NF;i++){print "<tr><td><p>" $i "</p></td></tr>"}}' >> $destFile

 		continue
 	fi

 	isNewLine=`echo $line | grep -c "^$"`
 	if [ $isNewLine ]; then
 		echo "</table></p><br></body></html>" >> $destFile
 		echo
 		continue
 	fi
 	
done
	
echo
