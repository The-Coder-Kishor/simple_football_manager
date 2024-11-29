-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.4.0-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.5.0.6677
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Dumping structure for table dnaproj4.captain
CREATE TABLE IF NOT EXISTS `captain` (
  `PlayerID` int(11) NOT NULL,
  `CaptainWinningRate` float DEFAULT NULL,
  `CaptainBonus` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`PlayerID`),
  CONSTRAINT `captain_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.clubs
CREATE TABLE IF NOT EXISTS `clubs` (
  `ClubID` int(11) NOT NULL AUTO_INCREMENT,
  `ClubName` varchar(255) DEFAULT NULL,
  `FoundationDate` date DEFAULT NULL,
  `Prestige` int(11) DEFAULT NULL,
  `Budget` decimal(15,2) DEFAULT NULL,
  `HomeStadiumID` int(11) DEFAULT NULL,
  `ManagerID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ClubID`),
  KEY `clubs_ibfk_1` (`HomeStadiumID`),
  KEY `clubs_ibfk_2` (`ManagerID`),
  CONSTRAINT `clubs_ibfk_1` FOREIGN KEY (`HomeStadiumID`) REFERENCES `stadiums` (`StadiumID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `clubs_ibfk_2` FOREIGN KEY (`ManagerID`) REFERENCES `managers` (`ManagerID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.contracts
CREATE TABLE IF NOT EXISTS `contracts` (
  `ContractID` int(11) NOT NULL AUTO_INCREMENT,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Salary` decimal(15,2) DEFAULT NULL,
  `Validity` tinyint(1) DEFAULT NULL,
  `ClubID` int(11) DEFAULT NULL,
  `PlayerID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ContractID`),
  KEY `contracts_ibfk_1` (`ClubID`),
  KEY `contracts_ibfk_2` (`PlayerID`),
  CONSTRAINT `contracts_ibfk_1` FOREIGN KEY (`ClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `contracts_ibfk_2` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.injuryrecord
CREATE TABLE IF NOT EXISTS `injuryrecord` (
  `InjuryID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerID` int(11) DEFAULT NULL,
  `InjuryDate` date DEFAULT NULL,
  `Severity` varchar(50) DEFAULT NULL,
  `RecurrenceRate` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`InjuryID`),
  KEY `injuryrecord_ibfk_1` (`PlayerID`),
  KEY `recoverypred` (`Severity`,`RecurrenceRate`),
  CONSTRAINT `injuryrecord_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `recoverypred` FOREIGN KEY (`Severity`, `RecurrenceRate`) REFERENCES `recoveryprediction` (`Severity`, `RecurrenceRate`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.leaguedetails
CREATE TABLE IF NOT EXISTS `leaguedetails` (
  `LeagueName` varchar(255) NOT NULL,
  `Nation` varchar(255) DEFAULT NULL,
  `NoOfTeams` int(11) DEFAULT NULL,
  `PromotionLevel` int(11) DEFAULT NULL,
  `RelegationLevel` int(11) DEFAULT NULL,
  PRIMARY KEY (`LeagueName`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.leagues
CREATE TABLE IF NOT EXISTS `leagues` (
  `LeagueID` int(11) NOT NULL AUTO_INCREMENT,
  `LeagueName` varchar(255) DEFAULT NULL,
  `LeagueYear` year(4) DEFAULT NULL,
  `UpperLeagueID` int(11) DEFAULT NULL,
  `LowerLeagueID` int(11) DEFAULT NULL,
  `WinningClubID` int(11) DEFAULT NULL,
  `TopScorerID` int(11) DEFAULT NULL,
  `TopAssistID` int(11) DEFAULT NULL,
  `TopCleanSheetID` int(11) DEFAULT NULL,
  PRIMARY KEY (`LeagueID`),
  KEY `leagues_ibfk_1` (`LeagueName`),
  KEY `leagues_ibfk_2` (`UpperLeagueID`),
  KEY `leagues_ibfk_3` (`LowerLeagueID`),
  KEY `leagues_ibfk_4` (`WinningClubID`),
  KEY `leagues_ibfk_5` (`TopScorerID`),
  KEY `leagues_ibfk_6` (`TopAssistID`),
  KEY `leagues_ibfk_7` (`TopCleanSheetID`),
  CONSTRAINT `leagues_ibfk_1` FOREIGN KEY (`LeagueName`) REFERENCES `leaguedetails` (`LeagueName`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_2` FOREIGN KEY (`UpperLeagueID`) REFERENCES `leagues` (`LeagueID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_3` FOREIGN KEY (`LowerLeagueID`) REFERENCES `leagues` (`LeagueID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_4` FOREIGN KEY (`WinningClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_5` FOREIGN KEY (`TopScorerID`) REFERENCES `players` (`PlayerID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_6` FOREIGN KEY (`TopAssistID`) REFERENCES `players` (`PlayerID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `leagues_ibfk_7` FOREIGN KEY (`TopCleanSheetID`) REFERENCES `players` (`PlayerID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.loanplayer
CREATE TABLE IF NOT EXISTS `loanplayer` (
  `PlayerID` int(11) NOT NULL,
  `JoinDate` date DEFAULT NULL,
  `ContractEnd` date DEFAULT NULL,
  `OriginalClubID` int(11) DEFAULT NULL,
  PRIMARY KEY (`PlayerID`),
  KEY `loanplayer_ibfk_2` (`OriginalClubID`),
  CONSTRAINT `loanplayer_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `loanplayer_ibfk_2` FOREIGN KEY (`OriginalClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.managerachievements
CREATE TABLE IF NOT EXISTS `managerachievements` (
  `AchievementID` int(11) NOT NULL AUTO_INCREMENT,
  `ManagerID` int(11) DEFAULT NULL,
  `AchievementDescription` text DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `ClubID` int(11) DEFAULT NULL,
  `LeagueID` int(11) DEFAULT NULL,
  PRIMARY KEY (`AchievementID`),
  KEY `managerachievements_ibfk_1` (`ManagerID`),
  KEY `managerachievements_ibfk_2` (`ClubID`),
  KEY `managerachievements_ibfk_3` (`LeagueID`),
  CONSTRAINT `managerachievements_ibfk_1` FOREIGN KEY (`ManagerID`) REFERENCES `managers` (`ManagerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `managerachievements_ibfk_2` FOREIGN KEY (`ClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `managerachievements_ibfk_3` FOREIGN KEY (`LeagueID`) REFERENCES `leagues` (`LeagueID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.managermatchperformance
CREATE TABLE IF NOT EXISTS `managermatchperformance` (
  `ManagerID` int(11) NOT NULL,
  `MatchID` int(11) NOT NULL,
  `ManagerPerformance` decimal(5,2) DEFAULT NULL,
  `TeamTacticID` int(11) DEFAULT NULL,
  `OpponentTacticID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ManagerID`,`MatchID`),
  KEY `managermatchperformance_ibfk_2` (`MatchID`),
  KEY `managermatchperformance_ibfk_3` (`TeamTacticID`),
  KEY `managermatchperformance_ibfk_4` (`OpponentTacticID`),
  CONSTRAINT `managermatchperformance_ibfk_1` FOREIGN KEY (`ManagerID`) REFERENCES `managers` (`ManagerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `managermatchperformance_ibfk_2` FOREIGN KEY (`MatchID`) REFERENCES `matchx` (`MatchID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `managermatchperformance_ibfk_3` FOREIGN KEY (`TeamTacticID`) REFERENCES `tactics` (`TacticID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `managermatchperformance_ibfk_4` FOREIGN KEY (`OpponentTacticID`) REFERENCES `tactics` (`TacticID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.managernationality
CREATE TABLE IF NOT EXISTS `managernationality` (
  `ManagerNationalityID` int(11) NOT NULL AUTO_INCREMENT,
  `ManagerID` int(11) DEFAULT NULL,
  `Nationality` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ManagerNationalityID`),
  KEY `managernationality_ibfk_1` (`ManagerID`),
  CONSTRAINT `managernationality_ibfk_1` FOREIGN KEY (`ManagerID`) REFERENCES `managers` (`ManagerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.managers
CREATE TABLE IF NOT EXISTS `managers` (
  `ManagerID` int(11) NOT NULL AUTO_INCREMENT,
  `ManagerName` varchar(255) DEFAULT NULL,
  `Experience` int(11) DEFAULT NULL,
  `Salary` decimal(15,2) DEFAULT NULL,
  `PreferredTacticID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ManagerID`),
  KEY `managers_ibfk_1` (`PreferredTacticID`),
  CONSTRAINT `managers_ibfk_1` FOREIGN KEY (`PreferredTacticID`) REFERENCES `tactics` (`TacticID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.matchx
CREATE TABLE IF NOT EXISTS `matchx` (
  `MatchID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date DEFAULT NULL,
  `HomeGoals` int(11) DEFAULT NULL,
  `AwayGoals` int(11) DEFAULT NULL,
  `NoOfAttendees` int(11) DEFAULT NULL,
  `HomeTeamID` int(11) DEFAULT NULL,
  `AwayTeamID` int(11) DEFAULT NULL,
  `LeagueID` int(11) DEFAULT NULL,
  `StadiumID` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchID`),
  KEY `matchx_ibfk_3` (`LeagueID`),
  KEY `matchx_ibfk_4` (`StadiumID`),
  KEY `matchx_ibfk_1` (`HomeTeamID`),
  KEY `matchx_ibfk_2` (`AwayTeamID`),
  CONSTRAINT `matchx_ibfk_1` FOREIGN KEY (`HomeTeamID`) REFERENCES `clubs` (`ClubID`) ON UPDATE CASCADE,
  CONSTRAINT `matchx_ibfk_2` FOREIGN KEY (`AwayTeamID`) REFERENCES `clubs` (`ClubID`) ON UPDATE CASCADE,
  CONSTRAINT `matchx_ibfk_3` FOREIGN KEY (`LeagueID`) REFERENCES `leagues` (`LeagueID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `matchx_ibfk_4` FOREIGN KEY (`StadiumID`) REFERENCES `stadiums` (`StadiumID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.playerlanguagespoken
CREATE TABLE IF NOT EXISTS `playerlanguagespoken` (
  `PlayerLanguageID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerID` int(11) DEFAULT NULL,
  `Language` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`PlayerLanguageID`),
  KEY `playerlanguagespoken_ibfk_1` (`PlayerID`),
  CONSTRAINT `playerlanguagespoken_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.playermatchperformance
CREATE TABLE IF NOT EXISTS `playermatchperformance` (
  `PlayerID` int(11) NOT NULL,
  `MatchID` int(11) NOT NULL,
  `PassAccuracy` decimal(5,2) DEFAULT NULL,
  `DistanceCovered` decimal(10,2) DEFAULT NULL,
  `MinutesPlayed` int(11) DEFAULT NULL,
  `Goals` int(11) DEFAULT NULL,
  `Assists` int(11) DEFAULT NULL,
  `Ratings` decimal(3,1) DEFAULT NULL,
  PRIMARY KEY (`PlayerID`,`MatchID`),
  KEY `playermatchperformance_ibfk_2` (`MatchID`),
  CONSTRAINT `playermatchperformance_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `playermatchperformance_ibfk_2` FOREIGN KEY (`MatchID`) REFERENCES `matchx` (`MatchID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.playernationality
CREATE TABLE IF NOT EXISTS `playernationality` (
  `PlayerNationalityID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerID` int(11) DEFAULT NULL,
  `Nationality` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`PlayerNationalityID`),
  KEY `playernationality_ibfk_1` (`PlayerID`),
  CONSTRAINT `playernationality_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.playerpositionsplayed
CREATE TABLE IF NOT EXISTS `playerpositionsplayed` (
  `PlayerPositionID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerID` int(11) DEFAULT NULL,
  `Position` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`PlayerPositionID`),
  KEY `playerpositionsplayed_ibfk_1` (`PlayerID`),
  CONSTRAINT `playerpositionsplayed_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.players
CREATE TABLE IF NOT EXISTS `players` (
  `PlayerID` int(11) NOT NULL AUTO_INCREMENT,
  `PlayerName` varchar(255) DEFAULT NULL,
  `BirthDate` date DEFAULT NULL,
  `MarketValue` decimal(15,2) DEFAULT NULL,
  `Height` decimal(5,2) DEFAULT NULL,
  `Weight` decimal(5,2) DEFAULT NULL,
  `JerseyNumber` int(11) DEFAULT NULL,
  `OverallRating` decimal(3,1) DEFAULT NULL,
  `WorkRate` varchar(50) DEFAULT NULL,
  `Aggressiveness` int(11) DEFAULT NULL,
  `ClubID` int(11) DEFAULT NULL,
  `MentorID` int(11) DEFAULT NULL,
  PRIMARY KEY (`PlayerID`),
  KEY `players_ibfk_1` (`ClubID`),
  KEY `players_ibfk_2` (`MentorID`),
  CONSTRAINT `players_ibfk_1` FOREIGN KEY (`ClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `players_ibfk_2` FOREIGN KEY (`MentorID`) REFERENCES `players` (`PlayerID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.playsin
CREATE TABLE IF NOT EXISTS `playsin` (
  `ClubID` int(11) NOT NULL,
  `LeagueID` int(11) NOT NULL,
  `Points` int(11) DEFAULT NULL,
  PRIMARY KEY (`ClubID`,`LeagueID`),
  KEY `playsin_ibfk_2` (`LeagueID`),
  CONSTRAINT `playsin_ibfk_1` FOREIGN KEY (`ClubID`) REFERENCES `clubs` (`ClubID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `playsin_ibfk_2` FOREIGN KEY (`LeagueID`) REFERENCES `leagues` (`LeagueID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.recoveryprediction
CREATE TABLE IF NOT EXISTS `recoveryprediction` (
  `Severity` varchar(50) NOT NULL,
  `RecurrenceRate` decimal(5,2) NOT NULL,
  `DaysToRecovery` int(11) NOT NULL,
  PRIMARY KEY (`Severity`,`RecurrenceRate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.stadiums
CREATE TABLE IF NOT EXISTS `stadiums` (
  `StadiumID` int(11) NOT NULL AUTO_INCREMENT,
  `StadiumName` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `Capacity` int(11) DEFAULT NULL,
  `TicketFare` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`StadiumID`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.tactics
CREATE TABLE IF NOT EXISTS `tactics` (
  `TacticID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) DEFAULT NULL,
  `Instruction` text DEFAULT NULL,
  `Formation` varchar(50) DEFAULT NULL,
  `Style` varchar(255) DEFAULT NULL,
  `CreatorManagerID` int(11) DEFAULT NULL,
  PRIMARY KEY (`TacticID`),
  KEY `tactics_ibfk_1` (`CreatorManagerID`),
  CONSTRAINT `tactics_ibfk_1` FOREIGN KEY (`CreatorManagerID`) REFERENCES `managers` (`ManagerID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

-- Dumping structure for table dnaproj4.youthplayer
CREATE TABLE IF NOT EXISTS `youthplayer` (
  `PlayerID` int(11) NOT NULL,
  `AcademyJoinDate` date DEFAULT NULL,
  `ExpectedGraduation` date DEFAULT NULL,
  `YouthLevel` int(11) DEFAULT NULL,
  PRIMARY KEY (`PlayerID`),
  CONSTRAINT `youthplayer_ibfk_1` FOREIGN KEY (`PlayerID`) REFERENCES `players` (`PlayerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Data exporting was unselected.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
