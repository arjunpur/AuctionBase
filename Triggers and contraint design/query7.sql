select count(distinct Category) from Bids natural join Categories where Amount > 100;