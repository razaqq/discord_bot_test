BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `votes` (
	`game`	INTEGER,
	`game_details`	TEXT,
	`team1`	TEXT,
	`team2`	TEXT,
	`team1_score`	INTEGER,
	`team2_score`	INTEGER,
	`player_id`	INTEGER
);
CREATE TABLE IF NOT EXISTS `points` (
	`player_id`	INTEGER,
	`points`	INTEGER
);
CREATE TABLE IF NOT EXISTS `games` (
	`game`	INTEGER,
	`date`	INTEGER,
	`game_type`	TEXT,
	`game_details`	TEXT,
	`team1`	TEXT,
	`team2`	TEXT,
	`score`	TEXT
);
INSERT INTO `games` VALUES (1,'2018-06-14T15:00:00UTC+00:00','GROUP','A','Russia','Saudi Arabia','None:None');
INSERT INTO `games` VALUES (2,'2018-06-15T12:00:00UTC+00:00','GROUP','A','Egypt','Uruguay','None:None');
INSERT INTO `games` VALUES (17,'2018-06-19T18:00:00UTC+00:00','GROUP','A','Russia','Egypt','None:None');
INSERT INTO `games` VALUES (19,'2018-06-20T15:00:00UTC+00:00','GROUP','A','Uruguay','Saudi Arabia','None:None');
INSERT INTO `games` VALUES (34,'2018-06-25T14:00:00UTC+00:00','GROUP','A','Uruguay','Russia','None:None');
INSERT INTO `games` VALUES (33,'2018-06-25T14:00:00UTC+00:00','GROUP','A','Saudi Arabia','Egypt','None:None');
INSERT INTO `games` VALUES (4,'2018-06-15T18:00:00UTC+00:00','GROUP','B','Portugal','Spain','None:None');
INSERT INTO `games` VALUES (3,'2018-06-15T15:00:00UTC+00:00','GROUP','B','Morocco','Iran','None:None');
INSERT INTO `games` VALUES (18,'2018-06-20T12:00:00UTC+00:00','GROUP','B','Portugal','Morocco','None:None');
INSERT INTO `games` VALUES (20,'2018-06-20T18:00:00UTC+00:00','GROUP','B','Iran','Spain','None:None');
INSERT INTO `games` VALUES (36,'2018-06-25T18:00:00UTC+00:00','GROUP','B','Spain','Morocco','None:None');
INSERT INTO `games` VALUES (35,'2018-06-25T18:00:00UTC+00:00','GROUP','B','Iran','Portugal','None:None');
INSERT INTO `games` VALUES (5,'2018-06-16T10:00:00UTC+00:00','GROUP','C','France','Australia','None:None');
INSERT INTO `games` VALUES (7,'2018-06-16T16:00:00UTC+00:00','GROUP','C','Peru','Denmark','None:None');
INSERT INTO `games` VALUES (22,'2018-06-21T15:00:00UTC+00:00','GROUP','C','France','Peru','None:None');
INSERT INTO `games` VALUES (21,'2018-06-21T12:00:00UTC+00:00','GROUP','C','Denmark','Australia','None:None');
INSERT INTO `games` VALUES (38,'2018-06-26T14:00:00UTC+00:00','GROUP','C','Australia','Peru','None:None');
INSERT INTO `games` VALUES (37,'2018-06-26T14:00:00UTC+00:00','GROUP','C','Denmark','France','None:None');
INSERT INTO `games` VALUES (6,'2018-06-16T13:00:00UTC+00:00','GROUP','D','Argentina','Iceland','None:None');
INSERT INTO `games` VALUES (8,'2018-06-16T19:00:00UTC+00:00','GROUP','D','Croatia','Nigeria','None:None');
INSERT INTO `games` VALUES (23,'2018-06-21T18:00:00UTC+00:00','GROUP','D','Argentina','Croatia','None:None');
INSERT INTO `games` VALUES (25,'2018-06-22T15:00:00UTC+00:00','GROUP','D','Nigeria','Iceland','None:None');
INSERT INTO `games` VALUES (39,'2018-06-26T18:00:00UTC+00:00','GROUP','D','Nigeria','Argentina','None:None');
INSERT INTO `games` VALUES (40,'2018-06-26T18:00:00UTC+00:00','GROUP','D','Iceland','Croatia','None:None');
INSERT INTO `games` VALUES (11,'2018-06-17T18:00:00UTC+00:00','GROUP','E','Brazil','Switzerland','None:None');
INSERT INTO `games` VALUES (9,'2018-06-17T12:00:00UTC+00:00','GROUP','E','Costa Rica','Serbia','None:None');
INSERT INTO `games` VALUES (24,'2018-06-22T12:00:00UTC+00:00','GROUP','E','Brazil','Costa Rica','None:None');
INSERT INTO `games` VALUES (26,'2018-06-22T18:00:00UTC+00:00','GROUP','E','Serbia','Switzerland','None:None');
INSERT INTO `games` VALUES (43,'2018-06-27T18:00:00UTC+00:00','GROUP','E','Serbia','Brazil','None:None');
INSERT INTO `games` VALUES (44,'2018-06-27T18:00:00UTC+00:00','GROUP','E','Switzerland','Costa Rica','None:None');
INSERT INTO `games` VALUES (10,'2018-06-17T15:00:00UTC+00:00','GROUP','F','Germany','Mexico','None:None');
INSERT INTO `games` VALUES (12,'2018-06-18T12:00:00UTC+00:00','GROUP','F','Sweden','Korea Republic','None:None');
INSERT INTO `games` VALUES (29,'2018-06-23T18:00:00UTC+00:00','GROUP','F','Germany','Sweden','None:None');
INSERT INTO `games` VALUES (28,'2018-06-23T15:00:00UTC+00:00','GROUP','F','Korea Republic','Mexico','None:None');
INSERT INTO `games` VALUES (41,'2018-06-27T14:00:00UTC+00:00','GROUP','F','Mexico','Sweden','None:None');
INSERT INTO `games` VALUES (42,'2018-06-27T14:00:00UTC+00:00','GROUP','F','Korea Republic','Germany','None:None');
INSERT INTO `games` VALUES (13,'2018-06-18T15:00:00UTC+00:00','GROUP','G','Belgium','Panama','None:None');
INSERT INTO `games` VALUES (14,'2018-06-18T18:00:00UTC+00:00','GROUP','G','Tunisia','England','None:None');
INSERT INTO `games` VALUES (27,'2018-06-23T12:00:00UTC+00:00','GROUP','G','Belgium','Tunisia','None:None');
INSERT INTO `games` VALUES (30,'2018-06-24T12:00:00UTC+00:00','GROUP','G','England','Panama','None:None');
INSERT INTO `games` VALUES (47,'2018-06-28T18:00:00UTC+00:00','GROUP','G','Panama','Tunisia','None:None');
INSERT INTO `games` VALUES (48,'2018-06-28T18:00:00UTC+00:00','GROUP','G','England','Belgium','None:None');
INSERT INTO `games` VALUES (16,'2018-06-19T15:00:00UTC+00:00','GROUP','H','Poland','Senegal','None:None');
INSERT INTO `games` VALUES (15,'2018-06-19T12:00:00UTC+00:00','GROUP','H','Colombia','Japan','None:None');
INSERT INTO `games` VALUES (31,'2018-06-24T15:00:00UTC+00:00','GROUP','H','Japan','Senegal','None:None');
INSERT INTO `games` VALUES (32,'2018-06-24T18:00:00UTC+00:00','GROUP','H','Poland','Colombia','None:None');
INSERT INTO `games` VALUES (45,'2018-06-28T14:00:00UTC+00:00','GROUP','H','Japan','Poland','None:None');
INSERT INTO `games` VALUES (46,'2018-06-28T14:00:00UTC+00:00','GROUP','H','Senegal','Colombia','None:None');
INSERT INTO `games` VALUES (49,'2018-06-30T14:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (50,'2018-06-30T18:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (51,'2018-07-01T14:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (52,'2018-07-01T18:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (53,'2018-07-02T14:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (54,'2018-07-02T18:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (55,'2018-07-03T14:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (56,'2018-07-03T18:00:00UTC+00:00','KNOCKOUT','Round of 16','','','None:None');
INSERT INTO `games` VALUES (57,'2018-07-06T14:00:00UTC+00:00','KNOCKOUT','Quarter-finals','','','None:None');
INSERT INTO `games` VALUES (58,'2018-07-06T18:00:00UTC+00:00','KNOCKOUT','Quarter-finals','','','None:None');
INSERT INTO `games` VALUES (60,'2018-07-07T18:00:00UTC+00:00','KNOCKOUT','Quarter-finals','','','None:None');
INSERT INTO `games` VALUES (59,'2018-07-07T14:00:00UTC+00:00','KNOCKOUT','Quarter-finals','','','None:None');
INSERT INTO `games` VALUES (61,'2018-07-10T18:00:00UTC+00:00','KNOCKOUT','Semi-finals','','','None:None');
INSERT INTO `games` VALUES (62,'2018-07-11T18:00:00UTC+00:00','KNOCKOUT','Semi-finals','','','None:None');
INSERT INTO `games` VALUES (63,'2018-07-14T14:00:00UTC+00:00','KNOCKOUT','Third place','','','None:None');
INSERT INTO `games` VALUES (64,'2018-07-15T15:00:00UTC+00:00','KNOCKOUT','Final','','','None:None');
COMMIT;
