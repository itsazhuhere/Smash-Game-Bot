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
-- Table structure for table `tournamentdates`
--

DROP TABLE IF EXISTS `tournamentdates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tournamentdates` (
  `db_name` varchar(30) DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tournamentdates`
--

LOCK TABLES `tournamentdates` WRITE;
/*!40000 ALTER TABLE `tournamentdates` DISABLE KEYS */;
INSERT INTO `tournamentdates` VALUES ('GENESIS 3','2016-01-15'),('PAX Arena','2016-01-29'),('B.E.A.S.T 6','2016-02-19'),('Battle of the Five Gods','2016-03-17'),('Pound 2016','2016-04-02'),('Smash Summit 2','2016-04-21'),('Enthusiast Gaming Live Expo','2016-04-29'),('DreamHack Austin 2016','2016-05-06'),('Get On My Level 2016','2016-05-20'),('Smash \'N\' Splash 2','2016-06-11'),('Low Tier City 4','2016-06-18'),('CEO 2016','2016-06-24'),('WTFox 2','2016-07-01'),('EVO 2016','2016-07-15'),('B.E.A.S.T 5','2015-01-09'),('Paragon Orlando 2015','2015-01-17'),('Apex 2015','2015-01-30'),('I\'m Not Yelling!','2015-04-10'),('Sandstorm','2015-04-18'),('DrømmeLAN 4.5','2015-04-24'),('Press Start','2015-05-09'),('Battle Arena Melbourne 7','2015-05-22'),('Get On My Level 2015','2015-05-30'),('Smash \'N\' Splash','2015-06-13'),('CEO 2015','2015-06-27'),('FC Smash 15XR: Return','2015-07-04'),('WTFox','2015-07-10'),('EVO 2015','2015-07-17'),('Super Smash Con','2015-08-06'),('Heir II the Throne','2015-08-14'),('PAX Prime 2015','2015-08-28'),('Paragon Los Angeles 2015','2015-09-05'),('HTC Throwdown','2015-09-19'),('DreamHack London 2015','2015-09-19'),('Helix','2015-09-26'),('The Big House 5','2015-10-02'),('MLG World Finals 2015','2015-10-16'),('Smash Summit','2015-11-05'),('Eclipse','2015-11-14'),('DreamHack Winter 2015','2015-11-26'),('Apex 2014','2014-01-17'),('B.E.A.S.T 4','2014-02-12'),('Revival of Melee 7','2014-03-08'),('Get On My Level 2014','2014-05-10'),('Republic of Fighters 3','2014-05-17'),('Pat\'s House 2','2014-05-24'),('SKTAR 3','2014-05-31'),('Super SWEET','2014-06-07'),('MLG Anaheim 2014','2014-06-20'),('CEO 2014','2014-06-27'),('Kings of Cali 4','2014-07-05'),('EVO 2014','2014-07-11'),('Zenith 2014','2014-08-02'),('Tipped Off 10','2014-09-20'),('The Big House 4','2014-10-04'),('Do You Fox Wit It?','2014-11-15'),('Forte 2','2014-12-20'),('Apex 2013','2013-01-11'),('B.E.A.S.T 3','2013-04-03'),('Zenith 2013','2013-06-01'),('EVO 2013','2013-07-12'),('The Big House 3','2013-10-12'),('Revival of Melee 6','2013-11-16'),('Kings of Cali 3','2013-12-14');
/*!40000 ALTER TABLE `tournamentdates` ENABLE KEYS */;
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
