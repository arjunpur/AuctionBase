select count(UserID) from (select UserID from Bidders where Location = "New York" union select UserID from Sellers where Location = "New York");