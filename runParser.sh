#!/bin/bash
python parser.py ebay_data/items-*.json
rm items.dat
rm sellers.dat
rm sales.dat
rm categories.dat
rm bids.dat
rm bidders.dat
awk '!x[$0]++' items1.dat > items.dat
awk '!x[$0]++' sellers1.dat > sellers.dat
awk '!x[$0]++' sales1.dat > sales.dat
awk '!x[$0]++' categories1.dat > categories.dat
awk '!x[$0]++' bids1.dat > bids.dat
awk '!x[$0]++' bidders1.dat > bidders.dat

