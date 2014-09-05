select count(*) from (select ItemID, count(ItemID) cnt from Categories group by ItemID having cnt = 4);
