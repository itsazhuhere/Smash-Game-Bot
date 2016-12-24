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
-- Table structure for table `bracketnames`
--

DROP TABLE IF EXISTS `bracketnames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bracketnames` (
  `bracketvariant` varchar(50) DEFAULT NULL,
  `bracket` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bracketnames`
--

LOCK TABLES `bracketnames` WRITE;
/*!40000 ALTER TABLE `bracketnames` DISABLE KEYS */;
INSERT INTO `bracketnames` VALUES ('Grand Finals','Grand Finals'),('GF','Grand Finals'),('Grand Final','Grand Finals'),('Winner\'s Finals','Winner\'s Finals'),('WF','Winner\'s Finals'),('winners final','Winner\'s Finals'),('winner final','Winner\'s Finals'),('Loser\'s Finals','Loser\'s Finals'),('LF','Loser\'s Finals'),('losers final','Loser\'s Finals'),('loser final','Loser\'s Finals'),('Winner\'s Semifinals','Winner\'s Semifinals'),('WS','Winner\'s Semifinals'),('winners semi','Winner\'s Semifinals'),('winner semi','Winner\'s Semifinals'),('Loser\'s Semifinals','Loser\'s Semifinals'),('LS','Loser\'s Semifinals'),('losers semi','Loser\'s Semifinals'),('loser semi','Loser\'s Semifinals'),('Winner\'s Quarterfinals','Winner\'s Quarterfinals'),('WQ','Winner\'s Quarterfinals'),('winners quarter','Winner\'s Quarterfinals'),('winner quarter','Winner\'s Quarterfinals'),('Loser\'s Quarterfinals','Loser\'s Quarterfinals'),('LQ','Loser\'s Quarterfinals'),('losers quarter','Loser\'s Quarterfinals'),('loser quarter','Loser\'s Quarterfinals'),('Winner\'s Top 8','Winner\'s Top 8'),('Loser\'s Top 8','Loser\'s Top 8'),('Top 16','Top 16'),('ro16','Top 16'),('Top 24','Top 24'),('ro24','Top 24'),('Top 32','Top 32'),('ro32','Top 32'),('Top 48','Top 48'),('ro48','Top 48'),('Top 64','Top 64'),('ro64','Top 64'),('Top 96','Top 96'),('ro96','Top 96'),('Top 128','Top 128'),('Ro128','Top 128'),('Pools','Pools'),('pool','Pools');
/*!40000 ALTER TABLE `bracketnames` ENABLE KEYS */;
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
