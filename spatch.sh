#!/bin/bash

colors='#define gate 48\n#define tway 15766860\n'
pre=";Awesomesauce"
matches=( ( "lbl_p80.txt" "[LABELS]" ) ( "lin_p80.txt" ";APD: KPDX" ) )

sed -i "s/#define background 0/$pre$colors\\n#define background 0/g" $1
bar="[LABELS]"

for section in ${matches[@]}; do
	while read -r line; do
	if [[ line=~${section[1]} ]]; then
		while read -r awesome
		do
			echo $awesome
		done < ${section[0]}
	fi < $1
done
