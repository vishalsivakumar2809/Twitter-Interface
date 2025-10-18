-- Let's drop the tables in case they exist from previous runs
drop table if exists retweets;
drop table if exists mentions;
drop table if exists hashtags;
drop table if exists tweets;
drop table if exists follows;
drop table if exists includes;
drop table if exists lists;
drop table if exists users;

-- Create the tables
create table users (
  usr         int,
  pwd         char(4),
  name        char(20),
  email       char(15),
  city        char(12),
  timezone    float,
  primary key (usr)
);
create table follows (
  flwer       int,
  flwee       int,
  start_date  date,
  primary key (flwer,flwee),
  foreign key (flwer) references users,
  foreign key (flwee) references users
);
create table tweets (
  tid         int,
  writer      int,
  tdate       date,
  text        char(80),
  replyto     int,
  primary key (tid),
  foreign key (writer) references users,
  foreign key (replyto) references tweets
);
create table hashtags (
  term        char(10),
  primary key (term)
);
create table mentions (
  tid         int,
  term        char(10),
  primary key (tid,term),
  foreign key (tid) references tweets,
  foreign key (term) references hashtags
);
create table retweets (
  usr         int,
  tid         int,
  rdate       date,
  primary key (usr,tid),
  foreign key (usr) references users,
  foreign key (tid) references tweets
);
create table lists (
  lname        char(12),
  owner        int,
  primary key (lname),
  foreign key (owner) references users
);
create table includes (
  lname       char(12),
  member      int,
  primary key (lname,member),
  foreign key (lname) references lists,
  foreign key (member) references users
);


-- Let's enforce the foreign keys
PRAGMA FOREIGN_KEYS = ON;

--Application 1
insert into users values (10,'aaa','validusr','usr@email','Rome',1.0);
insert into users values (11,'aaa','existedusr','usr@email','Rome',1.0);
--case 2.3
insert into users values (1,'aaa','usr101','usr@email','Rome',1.0);
insert into users values (2,'aaa','101follow102','usr@email','Rome',1.0);
insert into users values (3,'aaa','101follow103','usr@email','Rome',1.0);
insert into users values (4,'aaa','101notfollow104','usr@email','Rome',1.0);
insert into users values (5,'aaa','101notfollow105','usr@email','Rome',1.0);
insert into users values (6,'aaa','101notfollow106','usr@email','Rome',1.0);

insert into users values (7,'aaa','usr107','usr@email','Rome',1.0);
insert into users values (8,'aaa','usr108','usr@email','Rome',1.0);
insert into users values (9,'aaa','usr109','usr@email','Rome',1.0);



--
insert into follows values (1,2,'01-SEP-2022');
insert into follows values (1,3,'01-SEP-2022');

--first 5
insert into tweets values (10201,2,'21-AUG-2022','tweet1 of usr101 followee',null);
insert into tweets values (10202,2,'20-AUG-2022','tweet2 of usr101 followee',null);
insert into tweets values (10203,2,'19-AUG-2022','tweet3 of usr101 followee',null);
insert into tweets values (10301,3,'18-AUG-2022','tweet4 of usr101 followee',null);
insert into tweets values (10302,3,'17-AUG-2022','tweet5 of usr101 followee',null);

insert into tweets values (10401,4,'02-AUG-2020','retweet7 of usr101 followee',null);
insert into tweets values (10402,4,'03-AUG-2020','retweet8 of usr101 followee',null);
insert into tweets values (10403,4,'04-AUG-2020','retweet10 of usr101 followee',null);

--second 5
insert into tweets values (10303,3,'16-AUG-2022','tweet6 of usr101 followee',null);
insert into retweets values (3,10401,'15-AUG-2022');
insert into retweets values (3,10402,'14-AUG-2022');
insert into tweets values (10304,3,'13-AUG-2022','tweet9 of usr101 followee',null);
insert into retweets values (2,10403,'12-AUG-2022');

--3 retweets for tweets9
insert into retweets values (6,10304,'14-AUG-2022');
insert into retweets values (5,10304,'14-AUG-2022');
insert into retweets values (4,10304,'14-AUG-2022');

--6 replies for tweets9
insert into tweets values (10501,5,'14-AUG-2022','reply501 to tweet9',10304);
insert into tweets values (10502,5,'14-AUG-2022','reply502 to tweet9',10304);
insert into tweets values (10503,5,'14-AUG-2022','reply503 to tweet9',10304);
insert into tweets values (10601,6,'14-AUG-2022','reply601 to tweet9',10304);
insert into tweets values (10602,6,'14-AUG-2022','reply602 to tweet9',10304);
insert into tweets values (10603,6,'14-AUG-2022','reply603 to tweet9',10304);


--Application 2
insert into hashtags values ('edmonton');
insert into hashtags values ('jobs');
insert into hashtags values ('oilers');


--search hashtag Edmonton
--search context Edmonton
insert into tweets values (10701,7,'15-AUG-2022','tweet1 with keyword hashtag',null);
insert into tweets values (10702,7,'14-AUG-2022','tweet2 with keyword hashtag Edmonton',null);
insert into tweets values (10703,7,'13-AUG-2022','tweet3 with keyword hashtag edmonton',null);
insert into mentions values (10701,'edmonton');
insert into mentions values (10702,'edmonton');
insert into mentions values (10703,'edmonton');

insert into tweets values (10704,7,'12-AUG-2022','tweet4 without keyword hashtag edmonton but oilers',null);
insert into tweets values (10705,7,'11-AUG-2022','tweet5 with context Edmonton and hashtag jobs',null);
insert into mentions values (10704,'oilers');
insert into mentions values (10705,'jobs');

insert into tweets values (10706,7,'10-AUG-2022','tweet6 with context Edmonton',null);
insert into tweets values (10707,7,'09-AUG-2022','tweet7 with context Edmonton',null);
insert into tweets values (10708,7,'08-AUG-2022','tweet8 with context Edmonton',null);

insert into tweets values (10709,7,'07-AUG-2022','tweet9 with context oilers',null);
insert into tweets values (10710,7,'06-AUG-2022','tweet10 with context jobs',null);


--see statistic tweet10707
--2 retweets for tweet10707
insert into retweets values (8,10707,'14-AUG-2022');
insert into retweets values (9,10707,'14-AUG-2022');

--6 replies for tweet10707
insert into tweets values (10801,8,'14-AUG-2022','reply801 to tweet7',10707);
insert into tweets values (10802,8,'14-AUG-2022','reply802 to tweet7',10707);
insert into tweets values (10803,8,'14-AUG-2022','reply803 to tweet7',10707);
insert into tweets values (10901,9,'14-AUG-2022','reply901 to tweet7',10707);
insert into tweets values (10902,9,'14-AUG-2022','reply902 to tweet7',10707);
insert into tweets values (10903,9,'14-AUG-2022','reply903 to tweet7',10707);


--Application3
insert into users values (21,'aaa','usr121ABCD','usr@email','UVWXYZ',1.0);
insert into users values (22,'aaa','usr122ABCDE','usr@email','VWXYZ',1.0);
insert into users values (23,'aaa','usr123ABCDEF','usr@email','WXYZ',1.0);
insert into users values (24,'aaa','usr124ABCDEDG','usr@email','XYZ',1.0);

insert into users values (25,'aaa','usr125JKL','usr@email','Rome',1.0);
insert into users values (26,'aaa','usr126JKLM','usr@email','Rome',1.0);
insert into users values (27,'aaa','usr127JKLMN','usr@email','Rome',1.0);
insert into users values (28,'aaa','usr128JKLMNO','usr@email','JKLMNOP',1.0);
insert into users values (29,'aaa','usr129','usr@email','JKLM',1.0);
insert into users values (30,'aaa','usr130','usr@email','JKLMN',1.0);
insert into users values (31,'aaa','usr131','usr@email','JKLMNO',1.0);


---129 follows 125,126,127,128
insert into follows values (29,25,'01-SEP-2022');
insert into follows values (29,26,'01-SEP-2022');
insert into follows values (29,27,'01-SEP-2022');
insert into follows values (29,28,'01-SEP-2022');

---130,131 follow 129
insert into follows values (30,29,'01-SEP-2022');
insert into follows values (31,29,'01-SEP-2022');


insert into tweets values (12901,29,'07-SEP-2022','tweet1 of usr129',null);
insert into tweets values (12902,29,'08-SEP-2022','tweet2 of usr129',null);
insert into tweets values (12903,29,'09-SEP-2022','tweet3 of usr129',null);
insert into tweets values (12904,29,'10-SEP-2022','tweet4 of usr129',null);
insert into tweets values (12905,29,'11-SEP-2022','tweet5 of usr129',null);

--Application 4
insert into hashtags values ('survivor');
insert into hashtags values ('dba');


--Application5
insert into users values (12,'aaa','112follow101','usr@email','Rome',1.0);
insert into users values (13,'aaa','113follow101','usr@email','Rome',1.0);
insert into users values (14,'aaa','114follow101','usr@email','Rome',1.0);
insert into users values (15,'aaa','115follow101','usr@email','Rome',1.0);
insert into users values (16,'aaa','116follow101','usr@email','Rome',1.0);
insert into users values (17,'aaa','117follow101','usr@email','Rome',1.0);
insert into users values (18,'aaa','118follow101','usr@email','Rome',1.0);
insert into users values (19,'aaa','119follow101','usr@email','Rome',1.0);
insert into users values (20,'aaa','120follow101','usr@email','Rome',1.0);
insert into follows values (12,1,'01-SEP-2022');
insert into follows values (13,1,'01-SEP-2022');
insert into follows values (14,1,'01-SEP-2022');
insert into follows values (15,1,'01-SEP-2022');

--15 follow 1, 12,13,14
--15 is followed by 12, 13, 14
insert into follows values (15,12,'01-SEP-2022');
insert into follows values (15,13,'01-SEP-2022');
insert into follows values (15,14,'01-SEP-2022');

insert into follows values (12,15,'01-SEP-2022');
insert into follows values (13,15,'01-SEP-2022');
insert into follows values (14,15,'01-SEP-2022');

insert into tweets values (11501,15,'07-SEP-2022','tweet1 of usr115',null);
insert into tweets values (11502,15,'08-SEP-2022','tweet2 of usr115',null);
insert into tweets values (11503,15,'09-SEP-2022','tweet3 of usr115',null);
insert into tweets values (11504,15,'10-SEP-2022','tweet4 of usr115',null);
insert into tweets values (11505,15,'11-SEP-2022','tweet5 of usr115',null);


--lists 
insert into lists values ('usr101list1',1);
insert into lists values ('usr101list2',1);
insert into lists values ('usr112list',12);
insert into lists values ('usr113list',13);
insert into lists values ('usr114list',14);

-- list members owned by usr101
insert into includes values ('usr101list1',12);
insert into includes values ('usr101list1',13);
insert into includes values ('usr101list2',14);
insert into includes values ('usr101list2',15);

-- lists containting usr101
insert into includes values ('usr112list',1);
insert into includes values ('usr112list',15);
insert into includes values ('usr113list',1);
insert into includes values ('usr113list',15);

--list without usr101
insert into includes values ('usr114list',15);