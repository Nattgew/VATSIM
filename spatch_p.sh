#!/bin/bash

function unregex {
   # This is a function because dealing with quotes is a pain.
   # http://stackoverflow.com/a/2705678/120999
   sed -e 's/[]\/()$*.^|[]/\\&/g' <<< "$1" #whenyoudontwantregexbuttheymakeyouuseitanyway
}
function fsed {
   local find=$(unregex "$1")
   local replace=$(unregex "$2")
   shift 2 #This is so the positional parameter thingies work right
   # sed -i is only supported in GNU sed.
   # I don't really care but whatever
   #sed -i "s/$find/$replace/g" "$@"
   #perl -i -pe "s/\\Q${APP_NAME}/\\Q${APP_NAME}/g" txtfile.txt
   perl -p -i -e "s/$find/$replace/g" "$@"
}

colors='#define gate 48\n#define tway 15766860'
pre=";Awesomesauce"  #Header to make added content easily located

#Add colors to top of file
#sed -i "s/#define background 0/$pre\\n$colors\\n\\n&/g" "$1"
$(fsed "#define background 0" "$pre\\n$colors\\n\\n#define background 0" "$1")

#Comment out lines listed in the rem file
while read -r stricken; do
	#sed -i "s/$stricken/; &/g" "$1"
	$(fsed "$stricken" "; $stricken" "$1")
done < "rem_p80.txt"

#Define files with new content and the label under which they should be inserted
matches=("lbl_p80.txt" "[LABELS]" "lin_p80.txt" ";APD: KPDX")
#Loop through the files/matches to insert the new stuff
i=0
while [ $i -lt 4 ]; do
	while read -r line; do
		if [[ $line =~ ${matches[$((i+1))]} ]]; then
			echo "$pre\\n" #Put the comment label in first
			while read -r awesome; do
				echo "$awesome"
			done < "${matches[$i]}"
		fi 
	done < "$1"
	i=$((i+2))
done
