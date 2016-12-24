select distinct player1 from games;
select * from games where gametype = "Unknown";

select * from games where tournament like "%CB2016%";

select * from games where tournament = "B.E.A.S.T 5 ";

select distinct tournament from games;

select count(*) from games where bracket like "%SSBM%";


delete from games where bracket like "%Brawlhalla%" limit 29;

delete from tournaments where name = "NONE" limit 1;
update games set tournament = "CB 2016",bracket="SSBM Pools" where tournament="CB2016 Pools";

select * from tournaments;

select * from tournamentdates;

truncate games;
truncate tournamentdates;
truncate tournaments;

INSERT INTO tournamentdates (db_name, date) VALUES ("Do You Fox Wit It?",'2014-11-15');

ALTER TABLE games DROP column tournamentdate;

