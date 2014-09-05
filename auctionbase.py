#!/usr/bin/env python
import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid', 'add_bid',
        '/search', 'search',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class search:
    def GET(self):
        return render_template('search.html', winner = "N/A")
    def POST(self):
        post_params = web.input()
        item_id = post_params['itemID']
        user_id = post_params['userID']
        min_price = post_params['minPrice']
        max_price = post_params['maxPrice']
        category = post_params['category']
        status = post_params['status']
        search_result = [status]
        src1 = ""
        src2 = ""
        src3 = ""
        src4 = ""
        src5 = ""
        src6 = ""
        itemId = ""
        minPrice = ""
        maxPrice = ""
        winnerStr = ""

        currTime = sqlitedb.getTime()
        if (item_id != ""):
            itemId = int(item_id)
            src1 = " (select ItemID from Items where ItemID = $itemId) "
        
        if (user_id != ""):
            src2 = " (select ItemID from Sales where UserID = $userId) "
        
        if (min_price != ""):
            minPrice = float(min_price)
            src3 = " (select ItemID from Items where Currently > $minPrice) "
        if (max_price != ""):
            maxPrice = float(max_price)
            src4 = " (select ItemID from Items where Currently < $maxPrice) "
        if (status == "open" ):
            src5 = " (select ItemID from Items where (Started < $currTime) and (Ends > $currTime)) "
        if (status == "close"):
            winnerStr = "select distinct ItemID, UserID as Winner from Bids where UserID in (select UserID from (select UserID, max(Amount) from Bids group by ItemID))"
            src5 = " (select ItemID from Items where ((Started < $currTime) and (Ends < $currTime)) or Currently > Buy_Price)"
        if (status == "notStarted"):
            src5 = " (select ItemID from Items where (Started > $currTime) and (Ends > $currTime)) "
        if (status == "all") :
            src5 = " (select ItemID from Items) "
        if (category != ""):
            src6 = " (select ItemID from Categories where (Category = $category)) "
        arr = [src1,src2,src3,src4,src5,src6]
        query_string = "select distinct * from Items inner join Sales on Items.ItemID = Sales.ItemID where Items.ItemID in"
        first = False
        for i in xrange(len(arr)):
            if first == False and arr[i] != "":
                first = True
                query_string += arr[i]
            elif arr[i] != "":
                query_string += "and Items.ItemID in" + arr[i]

        t = sqlitedb.transaction()
        if (winnerStr != ""):
            cols = "q1.ItemID,Ends,First_Bid,Name,Started,Number_of_Bids,UserID,Buy_Price,Currently,Description,Winner"
            query_string = "select distinct " + cols +  " from (" +query_string + ") q1 inner join (" + winnerStr + ") q2 on q1.ItemID = q2.ItemID"
        
        
        try:
            result = sqlitedb.query(query_string, {'userId' : user_id, 'itemId': itemId, 'maxPrice':maxPrice, 'minPrice': minPrice, 'currTime':currTime, 'category':category})
            search_result = result
        except Exception as e:
            search_result = []

        else:
            t.commit()

            


        return render_template('search.html',search_result = search_result)




class add_bid:
    # Another GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('add_bid.html')

    def POST(self):
        post_params = web.input()
        item_id = int(post_params['itemID'])
        user_id = post_params['userID']
        price = float(post_params['price'])
        current_time = sqlitedb.getTime()
        test = "select * from Bids where (userID = $user_id) and (itemID = $item_id)"
        message = "A bid of $%s has been placed by %s for item %s" % (price,user_id,item_id)
        add_result = ""
        t = sqlitedb.transaction()
        try:
            started = sqlitedb.query("select Started from Items where ItemID = $item_id", {'item_id': item_id})
            ends = sqlitedb.query("select Ends from Items where ItemID = $item_id", {'item_id': item_id})
            buyPrice = sqlitedb.query("select Buy_Price from Items where ItemID = $item_id", {'item_id': item_id})[0].Buy_Price
            s = sqlitedb.query("select * from Bids where (ItemID = $item_id) and (Amount >= $buyPrice)",{'item_id': item_id, 'buyPrice': buyPrice})
            if (sqlitedb.isResultEmpty(s)):
                add_result = "done"
                sqlitedb.query("insert into Bids values ($user_id,$currTime,$price,$item_id)",
                    {'user_id':user_id,'currTime':current_time, 'price':price,'item_id':item_id, 'started': started[0].Started, 'ends': ends[0].Ends})
            
            else:
                message = "INSERT FAILED!"
                add_result = ""


        except Exception as e:
            message = str(e)
            add_result = ""
        else:
            t.commit()

        return render_template('add_bid.html',message = message, add_result = add_result)


class select_time:
    # Another GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        t = sqlitedb.transaction()
        try:
            sqlitedb.query('update CurrentTime set currTime = $time', {'time': selected_time})
        except Exception as e: 
            update_message = str(e)
            t.rollback()
        else:
            t.commit()
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
