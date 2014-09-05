
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS145 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""
import os.path
import sys
from json import loads
from re import sub


columnSeparator = "<>"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""

def deleteDuplicates():
    print("Deleting Duplicates")
    s = set()
    items = open("items.dat",'r')
    items1 = open("items1.dat",'w')
    sellers = open("sellers.dat",'r')
    sellers1 = open("sellers1.dat",'w')
    bidders = open("bidders.dat",'r')
    bidders1 = open("bidders1.dat",'w')
    bids = open("bids.dat",'r')
    bids1 = open("bids1.dat",'w')
    sales = open("sales.dat",'r')
    sales1 = open("sales1.dat",'w')
    categories = open("categories.dat",'r')
    categories1 = open("categories1.dat",'w')
    for line in items:
        if line not in s:
            items1.write(line)
            s.add(line)
    s = set()
    for line in sellers:
        if line not in s:
            sellers1.write(line)
            s.add(line)
    s = set()
    for line in bidders:
        if line not in s:
            bidders1.write(line)
            s.add(line)
    s = set()
    for line in bids:
        if line not in s:
            bids1.write(line)
            s.add(line)
    s = set()
    for line in sales:
        if line not in s:
            sales1.write(line)
            s.add(line)
    s = set()
    for line in categories:
        if line not in s:
            categories1.write(line)
            s.add(line)


    items.close()
    items1.close()
    sellers.close()
    sellers1.close()
    bidders.close()
    bidders1.close()
    sales.close()
    sales1.close()
    categories.close()
    categories1.close()



def parseJson(json_file):
    with open(json_file, 'r') as f:
        itemsAll = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        items = open("items.dat",'a')
        sellers = open("sellers.dat",'a')
        bidders = open("bidders.dat",'a')
        bids = open("bids.dat",'a')
        sales = open("sales.dat",'a')
        categories = open("categories.dat",'a') 
        for item in itemsAll:
            tempBid = ""
            tempBuyPrice = ""
            tempDescription = ""
            tempLoc = ""
            tempCount = ""
            tempRating = ""
            if ("Buy_Price" not in item or (item["Buy_Price"] is None)):
                tempBuyPrice = "NULL"
            
            else:
                tempBuyPrice = transformDollar(item["Buy_Price"])

            if ("Description" not in item or (item["Description"] is None)):
                tempDescription = "NULL"
            else:
                tempDescription = item["Description"]

            if ("Bids" not in item or (item["Bids"] is None)):
                tempBid = "NULL"
            else: 
                if ("Location" not in item["Bids"] or (item["Bids"]["Location"] is None)):
                    tempLoc = "NULL"
                else:
                    tempLoc = item["Bids"]["Location"]
                if ("Country" not in item["Bids"] or (item["Bids"]["Country"] is None)):
                    tempCount = "NULL"
                else:
                    tempCount = item["Bids"]["Location"]
                if ("Rating" not in item["Bids"] or (item["Bids"]["Rating"] is None)):
                    tempRating = "NULL"
                else:
                    tempRating = item["Bids"]["Rating"]
                

            items.write(item["ItemID"] + columnSeparator + item["Name"] + columnSeparator
                + transformDollar(item["Currently"]) + columnSeparator + tempBuyPrice + columnSeparator
                + transformDollar(item["First_Bid"]) + columnSeparator + item["Number_of_Bids"] + columnSeparator
                + transformDttm(item["Started"]) + columnSeparator + transformDttm(item["Ends"]) + columnSeparator 
                + tempDescription + '\n') 
            sellers.write(item["Seller"]["UserID"] + columnSeparator + item["Location"] + columnSeparator + item["Country"]
                + columnSeparator + item["Seller"]["Rating"] + '\n')
            sales.write(item["Seller"]["UserID"] + columnSeparator + item["ItemID"] + '\n')
            if (item["Bids"] is not None):
                for bid in item["Bids"]:
                    bid = bid["Bid"]
                    bidders.write(bid["Bidder"]["UserID"] + columnSeparator + tempLoc + columnSeparator + 
                        tempCount + columnSeparator+ tempRating + '\n')
                    bids.write(bid["Bidder"]["UserID"] + columnSeparator + transformDttm(bid["Time"]) + columnSeparator + transformDollar(bid["Amount"])
                        + columnSeparator + item["ItemID"] + '\n')
            for category in item["Category"]:
                categories.write(item["ItemID"] + columnSeparator + category + '\n')


        items.close()
        sellers.close()
        bidders.close()
        bids.close()
        sales.close()
        categories.close()





"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    try:
        os.remove("items.dat")
        os.remove("sellers.dat")
        os.remove("bidders.dat")
        os.remove("bids.dat")
        os.remove("sales.dat")
        os.remove("categories.dat")
        os.remove("items1.dat")
        os.remove("sellers1.dat")
        os.remove("bidders1.dat")
        os.remove("bids1.dat")
        os.remove("sales1.dat")
        os.remove("categories1.dat")
    except OSError:
        pass
    items = open("items.dat",'w')
    sellers = open("sellers.dat",'w')
    bidders = open("bidders.dat",'w')
    bids = open("bids.dat",'w')
    sales = open("sales.dat",'w')
    categories = open("categories.dat",'w')
    items.close()
    sellers.close()
    bidders.close()
    bids.close()
    sales.close()
    categories.close() 
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print "Success parsing " + f
    # items = open("items.dat",'r')
    # sellers = open("sellers.dat",'r')
    # bidders = open("bidders.dat",'r')
    # bids = open("bids.dat",'r')
    # sales = open("sales.dat",'r')
    # categories = open("categories.dat",'r') 

    # print("items: " + str(sum(1 for line in items if line.rstrip('\n'))))
    # print("sellers: " + str(sum(1 for line in sellers if line.rstrip('\n'))))
    # print("bidders: " + str(sum(1 for line in bidders if line.rstrip('\n'))))
    # print("bids: " + str(sum(1 for line in bids if line.rstrip('\n'))))
    # print("sales: " + str(sum(1 for line in sales if line.rstrip('\n'))))
    # print("cats: " + str(sum(1 for line in categories if line.rstrip('\n'))))
    deleteDuplicates()

if __name__ == '__main__':
    main(sys.argv)
