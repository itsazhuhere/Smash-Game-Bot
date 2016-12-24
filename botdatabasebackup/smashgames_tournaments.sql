-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: smashgames
-- ------------------------------------------------------
-- Server version	5.7.9-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tournaments`
--

DROP TABLE IF EXISTS `tournaments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tournaments` (
  `name` varchar(30) DEFAULT NULL,
  `db_name` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tournaments`
--

LOCK TABLES `tournaments` WRITE;
/*!40000 ALTER TABLE `tournaments` DISABLE KEYS */;
INSERT INTO `tournaments` VALUES ('GENESIS 3','GENESIS 3'),('PAX Arena','PAX Arena'),('PAX South Arena','PAX Arena'),('PAX','PAX Arena'),('B.E.A.S.T 6','B.E.A.S.T 6'),('BEAST 6','B.E.A.S.T 6'),('Battle of the Five Gods','Battle of the Five Gods'),('Pound 2016','Pound 2016'),('Pound 2016 Doubles','Pound 2016'),('Smash Summit 2','Smash Summit 2'),('Enthusiast Gaming Live Expo','Enthusiast Gaming Live Expo'),('EGLX','Enthusiast Gaming Live Expo'),('DreamHack Austin 2016','DreamHack Austin 2016'),('Dreamhack Smash 2016','DreamHack Austin 2016'),('Get On My Level 2016','Get On My Level 2016'),('GOML2016','Get On My Level 2016'),('Smash \'N\' Splash 2','Smash \'N\' Splash 2'),('SNS2','Smash \'N\' Splash 2'),('Low Tier City 4','Low Tier City 4'),('LTC4','Low Tier City 4'),('CEO 2016','CEO 2016'),('CEO 2016 Smash 4','CEO 2016'),('CEO 2016 SSBM','CEO 2016'),('WTFox 2','WTFox 2'),('EVO 2016','EVO 2016'),('B.E.A.S.T 5','B.E.A.S.T 5'),('Paragon Orlando 2015','Paragon Orlando 2015'),('Paragon 2015','Paragon Orlando 2015'),('Apex 2015','Apex 2015'),('I\'m Not Yelling!','I\'m Not Yelling!'),('INY Day 2','I\'m Not Yelling!'),('Sandstorm','Sandstorm'),('MVG Sandstorm','Sandstorm'),('DrømmeLAN 4.5','DrømmeLAN 4.5'),('DL4.5','DrømmeLAN 4.5'),('Press Start','Press Start'),('Press Start Day 1','Press Start'),('Press Start Day 2','Press Start'),('Battle Arena Melbourne 7','Battle Arena Melbourne 7'),('Bam 7','Battle Arena Melbourne 7'),('Get On My Level 2015','Get On My Level 2015'),('GOML 2015','Get On My Level 2015'),('Smash \'N\' Splash','Smash \'N\' Splash'),('SNS','Smash \'N\' Splash'),('CEO 2015','CEO 2015'),('FC Smash 15XR: Return','FC Smash 15XR: Return'),('FC Return','FC Smash 15XR: Return'),('WTFox','WTFox'),('EVO 2015','EVO 2015'),('Super Smash Con','Super Smash Con'),('SSC','Super Smash Con'),('Heir II the Throne','Heir II the Throne'),('Heir2','Heir II the Throne'),('PAX Prime 2015','PAX Prime 2015'),('Paragon Los Angeles 2015','Paragon Los Angeles 2015'),('HTC Throwdown','HTC Throwdown'),('DreamHack London 2015','DreamHack London 2015'),('Helix','Helix'),('The Big House 5','The Big House 5'),('TBH5','The Big House 5'),('TBH5 Smash 4','The Big House 5'),('MLG World Finals 2015','MLG World Finals 2015'),('MLG Finals','MLG World Finals 2015'),('MLG World Finals','MLG World Finals 2015'),('Smash Summit','Smash Summit'),('Eclipse','Eclipse'),('ECLIPSE 2015','Eclipse'),('DreamHack Winter 2015','DreamHack Winter 2015'),('Melee DHW15','DreamHack Winter 2015'),('Apex 2014','Apex 2014'),('Apex 2014 Tournament','Apex 2014'),('B.E.A.S.T 4','B.E.A.S.T 4'),('Revival of Melee 7','Revival of Melee 7'),('Get On My Level 2014','Get On My Level 2014'),('GOML','Get On My Level 2014'),('Republic of Fighters 3','Republic of Fighters 3'),('RoF#3','Republic of Fighters 3'),('Pat\'s House 2','Pat\'s House 2'),('PH2','Pat\'s House 2'),('SKTAR 3','SKTAR 3'),('Super SWEET','Super SWEET'),('MLG Anaheim 2014','MLG Anaheim 2014'),('CEO 2014','CEO 2014'),('Kings of Cali 4','Kings of Cali 4'),('KoC 4','Kings of Cali 4'),('EVO 2014','EVO 2014'),('Zenith 2014','Zenith 2014'),('Tipped Off 10','Tipped Off 10'),('TOX','Tipped Off 10'),('The Big House 4','The Big House 4'),('TBH4','The Big House 4'),('Do You Fox Wit It?','Do You Fox Wit It?'),('DYFWI Day 1','Do You Fox Wit It?'),('DYFWI Day 2','Do You Fox Wit It?'),('Forte 2','Forte 2'),('Forte 2 Melee','Forte 2'),('Apex 2013','Apex 2013'),('B.E.A.S.T 3','B.E.A.S.T 3'),('Beast 3','B.E.A.S.T 3'),('Zenith 2013','Zenith 2013'),('EVO 2013','EVO 2013'),('The Big House 3','The Big House 3'),('Revival of Melee 6','Revival of Melee 6'),('Kings of Cali 3','Kings of Cali 3');
/*!40000 ALTER TABLE `tournaments` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-10-18 15:29:13
