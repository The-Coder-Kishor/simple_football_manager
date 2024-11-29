import pymysql
import pymysql.cursors
from datetime import datetime, date
import sys

class FootballDatabaseSystem:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host="localhost",
                user="root",
                password="678007",
                database="dnaproj4",
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
        except pymysql.Error as err:
            print(f"Error: {err}")
            sys.exit(1)

    # INSERT Functions
    def insert_player(self):
        try:
            player_data = {
                'player_id': int(input("Player ID: ")),
                'name': input("Name: "),
                'birth_date': input("Birth Date (YYYY-MM-DD): "),
                'market_value': float(input("Market Value: ")),
                'club_id': int(input("Club ID: ")),
                'jersey_number': int(input("Jersey Number: ")),
                'overall_rating': float(input("Overall Rating: "))
            }
            
            query = """INSERT INTO Players 
                      (PlayerID, PlayerName, BirthDate, MarketValue, ClubID, JerseyNumber, OverallRating) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(player_data.values()))
            self.conn.commit()
            print("Player added successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def create_team(self):
        try:
            team_data = {
                'club_id': int(input("Club ID: ")),
                'name': input("Club Name: "),
                'foundation_date': input("Foundation Date (YYYY-MM-DD): "),
                'budget': float(input("Budget: ")),
                'stadium_id': int(input("Home Stadium ID: ")),
                'manager_id': int(input("Manager ID: "))
            }
            
            if team_data['budget'] < 0:
                raise ValueError("Budget cannot be negative")
                
            query = """INSERT INTO Clubs 
                      (ClubID, ClubName, FoundationDate, Budget, HomeStadiumID, ManagerID) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(team_data.values()))
            self.conn.commit()
            print("Team created successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def add_manager(self):
        try:
            manager_data = {
                'manager_id': int(input("Manager ID: ")),
                'name': input("Name: "),
                'experience': int(input("Experience (years): ")),
                'salary': float(input("Salary: ")),
                'preferred_tactic': int(input("Preferred Tactic ID: "))
            }
            
            if manager_data['experience'] < 0:
                raise ValueError("Experience cannot be negative")
                
            query = """INSERT INTO Managers 
                      (ManagerID, ManagerName, Experience, Salary, PreferredTacticID) 
                      VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(manager_data.values()))
            self.conn.commit()
            print("Manager added successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def create_match(self):
        try:
            match_data = {
                'match_id': int(input("Match ID: ")),
                'date': input("Match Date (YYYY-MM-DD): "),
                'home_team': int(input("Home Team ID: ")),
                'away_team': int(input("Away Team ID: ")),
                'league_id': int(input("League ID: ")),
                'stadium_id': int(input("Stadium ID: "))
            }
            
            # Check if teams have other matches on the same date
            check_query = """SELECT COUNT(*) FROM Match 
                           WHERE Date = %s AND (HomeTeamID = %s OR AwayTeamID = %s 
                           OR HomeTeamID = %s OR AwayTeamID = %s)"""
            self.cursor.execute(check_query, (match_data['date'], match_data['home_team'], 
                                            match_data['home_team'], match_data['away_team'], 
                                            match_data['away_team']))
            if self.cursor.fetchone()[0] > 0:
                raise ValueError("Team already has a match scheduled on this date")
                
            query = """INSERT INTO Match 
                      (MatchID, Date, HomeTeamID, AwayTeamID, LeagueID, StadiumID) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(match_data.values()))
            self.conn.commit()
            print("Match created successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def setup_contract(self):
        try:
            contract_data = {
                'contract_id': int(input("Contract ID: ")),
                'player_id': int(input("Player ID: ")),
                'club_id': int(input("Club ID: ")),
                'start_date': input("Start Date (YYYY-MM-DD): "),
                'end_date': input("End Date (YYYY-MM-DD): "),
                'salary': float(input("Salary: "))
            }
            
            if contract_data['salary'] <= 0:
                raise ValueError("Salary must be positive")
                
            if contract_data['start_date'] >= contract_data['end_date']:
                raise ValueError("End date must be after start date")
                
            query = """INSERT INTO Contracts 
                    (ContractID, PlayerID, ClubID, StartDate, EndDate, Salary, Validity) 
                    VALUES (%s, %s, %s, %s, %s, %s, TRUE)"""
            self.cursor.execute(query, tuple(contract_data.values()))
            self.conn.commit()
            print("Contract created successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def record_injury(self):
        try:
            injury_data = {
                'injury_id': int(input("Injury ID: ")),
                'player_id': int(input("Player ID: ")),
                'injury_date': input("Injury Date (YYYY-MM-DD): "),
                'severity': input("Severity (Minor/Moderate/Severe): "),
                'recurrence_rate': float(input("Recurrence Rate (0-100): "))
            }
            
            query = """INSERT INTO InjuryRecord 
                    (InjuryID, PlayerID, InjuryDate, Severity, RecurrenceRate) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(injury_data.values()))
            self.conn.commit()
            print("Injury recorded successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def create_tactic(self):
        try:
            tactic_data = {
                'tactic_id': int(input("Tactic ID: ")),
                'name': input("Tactic Name: "),
                'formation': input("Formation (e.g., 4-4-2): "),
                'style': input("Playing Style: "),
                'creator_manager_id': int(input("Creator Manager ID: "))
            }
            
            if not self.validate_formation(tactic_data['formation']):
                raise ValueError("Invalid formation format")
                
            query = """INSERT INTO Tactics 
                    (TacticID, Name, Formation, Style, CreatorManagerID) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(tactic_data.values()))
            self.conn.commit()
            print("Tactic created successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def add_youth_player(self):
        try:
            youth_data = {
                'player_id': int(input("Player ID: ")),
                'academy_join_date': input("Academy Join Date (YYYY-MM-DD): "),
                'expected_graduation': input("Expected Graduation (YYYY-MM-DD): "),
                'youth_level': int(input("Youth Level (1-5): "))
            }
            
            # First add to Players table
            player_data = {
                'player_id': youth_data['player_id'],
                'name': input("Player Name: "),
                'birth_date': input("Birth Date (YYYY-MM-DD): "),
                'club_id': int(input("Club ID: "))
            }
            
            # Calculate age
            birth_date = datetime.strptime(player_data['birth_date'], '%Y-%m-%d').date()
            age = (date.today() - birth_date).days / 365.25
            
            if not (12 <= age <= 20):
                raise ValueError("Youth player must be between 12 and 20 years old")
                
            # Insert into Players table first
            player_query = """INSERT INTO Players 
                            (PlayerID, PlayerName, BirthDate, ClubID) 
                            VALUES (%s, %s, %s, %s)"""
            self.cursor.execute(player_query, tuple(player_data.values()))
            
            # Then insert into YouthPlayer table
            youth_query = """INSERT INTO YouthPlayer 
                            (PlayerID, AcademyJoinDate, ExpectedGraduation, YouthLevel) 
                            VALUES (%s, %s, %s, %s)"""
            self.cursor.execute(youth_query, tuple(youth_data.values()))
            
            self.conn.commit()
            print("Youth player added successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def add_player_language(self):
        try:
            player_id = int(input("Player ID: "))
            language = input("Language: ")
            
            query = """INSERT INTO PlayerLanguageSpoken 
                    (PlayerID, Language) VALUES (%s, %s)"""
            self.cursor.execute(query, (player_id, language))
            self.conn.commit()
            print("Language added successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def add_player_language(self):
        try:
            player_id = int(input("Player ID: "))
            language = input("Language: ")
            
            query = """INSERT INTO PlayerLanguageSpoken 
                    (PlayerID, Language) VALUES (%s, %s)"""
            self.cursor.execute(query, (player_id, language))
            self.conn.commit()
            print("Language added successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")
            
    def register_captain(self):
        try:
            player_id = int(input("Player ID: "))
            winning_rate = float(input("Captain Winning Rate: "))
            bonus = float(input("Captain Bonus: "))
            
            if not (0 <= winning_rate <= 100):
                raise ValueError("Winning rate must be between 0 and 100")
                
            query = """INSERT INTO Captain 
                    (PlayerID, CaptainWinningRate, CaptainBonus) 
                    VALUES (%s, %s, %s)"""
            self.cursor.execute(query, (player_id, winning_rate, bonus))
            self.conn.commit()
            print("Captain registered successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def register_loan_player(self):
        try:
            loan_data = {
                'player_id': int(input("Player ID: ")),
                'join_date': input("Join Date (YYYY-MM-DD): "),
                'contract_end': input("Contract End Date (YYYY-MM-DD): "),
                'original_club_id': int(input("Original Club ID: "))
            }
            
            query = """INSERT INTO LoanPlayer 
                    (PlayerID, JoinDate, ContractEnd, OriginalClubID) 
                    VALUES (%s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(loan_data.values()))
            self.conn.commit()
            print("Loan player registered successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def record_manager_performance(self):
        try:
            performance_data = {
                'manager_id': int(input("Manager ID: ")),
                'match_id': int(input("Match ID: ")),
                'performance': float(input("Performance Rating (0-10): ")),
                'team_tactic': int(input("Team Tactic ID: ")),
                'opponent_tactic': int(input("Opponent Tactic ID: "))
            }
            
            if not (0 <= performance_data['performance'] <= 10):
                raise ValueError("Performance rating must be between 0 and 10")
                
            query = """INSERT INTO ManagerMatchPerformance 
                    (ManagerID, MatchID, ManagerPerformance, TeamTacticID, OpponentTacticID) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(performance_data.values()))
            self.conn.commit()
            print("Manager performance recorded successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def record_manager_achievement(self):
        try:
            achievement_data = {
                'achievement_id': int(input("Achievement ID: ")),
                'manager_id': int(input("Manager ID: ")),
                'description': input("Achievement Description: "),
                'date': input("Achievement Date (YYYY-MM-DD): "),
                'club_id': int(input("Club ID: ")),
                'league_id': int(input("League ID: "))
            }
            
            query = """INSERT INTO ManagerAchievements 
                    (AchievementID, ManagerID, AchievementDescription, Date, ClubID, LeagueID) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(achievement_data.values()))
            self.conn.commit()
            print("Manager achievement recorded successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")
    
    def add_league(self):
        try:
            league_data = {
                'league_id': int(input("League ID: ")),
                'name': input("League Name: "),
                'year': int(input("League Year: ")),
                'upper_league_id': input("Upper League ID (Enter 0 if none): ") or None,
                'lower_league_id': input("Lower League ID (Enter 0 if none): ") or None
            }
            
            query = """INSERT INTO Leagues 
                    (LeagueID, LeagueName, LeagueYear, UpperLeagueID, LowerLeagueID) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(league_data.values()))
            
            # Add league details
            details_data = {
                'league_id': league_data['league_id'],
                'nation': input("Nation: "),
                'teams': int(input("Number of Teams: ")),
                'promotion': int(input("Promotion Level: ")),
                'relegation': int(input("Relegation Level: "))
            }
            
            details_query = """INSERT INTO LeagueDetails 
                            (LeagueID, Nation, NoOfTeams, PromotionLevel, RelegationLevel) 
                            VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(details_query, tuple(details_data.values()))
            
            self.conn.commit()
            print("League added successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def add_stadium(self):
        try:
            stadium_data = {
                'stadium_id': int(input("Stadium ID: ")),
                'name': input("Stadium Name: "),
                'capacity': int(input("Capacity: ")),
                'ticket_fare': float(input("Ticket Fare: "))
            }
            
            if stadium_data['capacity'] <= 0:
                raise ValueError("Capacity must be positive")
            if stadium_data['ticket_fare'] <= 0:
                raise ValueError("Ticket fare must be positive")
                
            query = """INSERT INTO Stadiums 
                    (StadiumID, StadiumName, Capacity, TicketFare) 
                    VALUES (%s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(stadium_data.values()))
            self.conn.commit()
            print("Stadium added successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")





    # UPDATE Functions
    def update_player_stats(self):
        try:
            performance_data = {
                'player_id': int(input("Player ID: ")),
                'match_id': int(input("Match ID: ")),
                'goals': int(input("Goals Scored: ")),
                'assists': int(input("Assists: ")),
                'minutes_played': int(input("Minutes Played: ")),
                'rating': float(input("Match Rating (0-10): "))
            }
            
            query = """INSERT INTO PlayerMatchPerformance 
                    (PlayerID, MatchID, Goals, Assists, MinutesPlayed, Ratings) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, tuple(performance_data.values()))
            self.conn.commit()
            print("Player statistics updated successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def update_contract(self):
        try:
            contract_id = int(input("Contract ID to modify: "))
            new_salary = float(input("New Salary: "))
            new_end_date = input("New End Date (YYYY-MM-DD): ")
            
            if new_salary <= 0:
                raise ValueError("Salary must be positive")
                
            query = """UPDATE Contracts 
                    SET Salary = %s, EndDate = %s 
                    WHERE ContractID = %s"""
            self.cursor.execute(query, (new_salary, new_end_date, contract_id))
            self.conn.commit()
            print("Contract updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def update_tactics(self):
        try:
            tactic_id = int(input("Tactic ID to modify: "))
            new_formation = input("New Formation: ")
            new_style = input("New Style: ")
            
            if not self.validate_formation(new_formation):
                raise ValueError("Invalid formation format")
                
            query = """UPDATE Tactics 
                    SET Formation = %s, Style = %s 
                    WHERE TacticID = %s"""
            self.cursor.execute(query, (new_formation, new_style, tactic_id))
            self.conn.commit()
            print("Tactics updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def update_market_value(self):
        try:
            player_id = int(input("Player ID: "))
            new_value = float(input("New Market Value: "))
            
            if new_value < 0:
                raise ValueError("Market value cannot be negative")
                
            query = """UPDATE Players 
                    SET MarketValue = %s 
                    WHERE PlayerID = %s"""
            self.cursor.execute(query, (new_value, player_id))
            self.conn.commit()
            print("Market value updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def promote_youth_player(self):
        try:
            player_id = int(input("Youth Player ID to promote: "))
            
            # Remove from YouthPlayer table
            delete_query = "DELETE FROM YouthPlayer WHERE PlayerID = %s"
            self.cursor.execute(delete_query, (player_id,))
            
            # Update player status in Players table if needed
            update_query = """UPDATE Players 
                            SET OverallRating = %s 
                            WHERE PlayerID = %s"""
            initial_rating = float(input("Initial Senior Team Rating: "))
            self.cursor.execute(update_query, (initial_rating, player_id))
            
            self.conn.commit()
            print("Youth player promoted successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def update_team_budget(self):
        try:
            club_id = int(input("Club ID: "))
            new_budget = float(input("New Budget: "))
            
            if new_budget < 0:
                raise ValueError("Budget cannot be negative")
                
            query = """UPDATE Clubs 
                    SET Budget = %s 
                    WHERE ClubID = %s"""
            self.cursor.execute(query, (new_budget, club_id))
            self.conn.commit()
            print("Team budget updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def update_player_position(self):
        try:
            player_id = int(input("Player ID: "))
            position = input("New Position: ")
            
            valid_positions = ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST']
            if position not in valid_positions:
                raise ValueError("Invalid position")
                
            # First check if position exists
            check_query = """SELECT COUNT(*) FROM PlayerPositionsPlayed 
                            WHERE PlayerID = %s AND Position = %s"""
            self.cursor.execute(check_query, (player_id, position))
            
            if self.cursor.fetchone()[0] == 0:
                # Insert new position
                insert_query = """INSERT INTO PlayerPositionsPlayed 
                                (PlayerID, Position) VALUES (%s, %s)"""
                self.cursor.execute(insert_query, (player_id, position))
            
            self.conn.commit()
            print("Player position updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def update_injury_status(self):
        try:
            injury_id = int(input("Injury ID: "))
            new_severity = input("Updated Severity (Minor/Moderate/Severe): ")
            new_recurrence = float(input("Updated Recurrence Rate: "))
            
            query = """UPDATE InjuryRecord 
                    SET Severity = %s, RecurrenceRate = %s 
                    WHERE InjuryID = %s"""
            self.cursor.execute(query, (new_severity, new_recurrence, injury_id))
            self.conn.commit()
            print("Injury status updated successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")
        
    def update_league_standings(self):
        try:
            club_id = int(input("Club ID: "))
            league_id = int(input("League ID: "))
            points = int(input("Updated Points: "))
            
            query = """UPDATE PlaysIn 
                    SET Points = %s 
                    WHERE ClubID = %s AND LeagueID = %s"""
            self.cursor.execute(query, (points, club_id, league_id))
            self.conn.commit()
            print("League standings updated successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def update_league_details(self):
        try:
            league_id = int(input("League ID: "))
            teams = int(input("New Number of Teams: "))
            promotion = int(input("New Promotion Level: "))
            relegation = int(input("New Relegation Level: "))
            
            query = """UPDATE LeagueDetails 
                    SET NoOfTeams = %s, PromotionLevel = %s, RelegationLevel = %s 
                    WHERE LeagueID = %s"""
            self.cursor.execute(query, (teams, promotion, relegation, league_id))
            self.conn.commit()
            print("League details updated successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")
    
    def update_stadium(self):
        try:
            stadium_id = int(input("Stadium ID: "))
            capacity = int(input("New Capacity: "))
            fare = float(input("New Ticket Fare: "))
            
            if capacity <= 0 or fare <= 0:
                raise ValueError("Capacity and fare must be positive")
                
            query = """UPDATE Stadiums 
                    SET Capacity = %s, TicketFare = %s 
                    WHERE StadiumID = %s"""
            self.cursor.execute(query, (capacity, fare, stadium_id))
            self.conn.commit()
            print("Stadium updated successfully!")
        except (pymysql.Error, ValueError) as err:
            print(f"Error: {err}")

    def update_match_details(self):
        try:
            match_id = int(input("Match ID: "))
            home_goals = int(input("Home Goals: "))
            away_goals = int(input("Away Goals: "))
            attendees = int(input("Number of Attendees: "))
            
            query = """UPDATE Match 
                    SET HomeGoals = %s, AwayGoals = %s, NoOfAttendees = %s 
                    WHERE MatchID = %s"""
            self.cursor.execute(query, (home_goals, away_goals, attendees, match_id))
            self.conn.commit()
            print("Match details updated successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")
    
    
    
    
# DELETE Functions
    def delete_expired_contracts(self):
        try:
            current_date = date.today()
            query = """DELETE FROM Contracts 
                    WHERE EndDate < %s"""
            self.cursor.execute(query, (current_date,))
            self.conn.commit()
            print(f"Deleted {self.cursor.rowcount} expired contracts!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def delete_completed_matches(self):
        try:
            current_date = date.today()
            query = """DELETE FROM Match 
                    WHERE Date < %s"""
            self.cursor.execute(query, (current_date,))
            self.conn.commit()
            print(f"Deleted {self.cursor.rowcount} completed matches!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def remove_healed_players(self):
        try:
            current_date = date.today()
            query = """DELETE FROM InjuryRecord 
                    WHERE InjuryDate + INTERVAL 
                    (SELECT DaysToRecovery FROM RecoveryPrediction 
                    WHERE Severity = InjuryRecord.Severity 
                    AND RecurrenceRate = InjuryRecord.RecurrenceRate) DAY < %s"""
            self.cursor.execute(query, (current_date,))
            self.conn.commit()
            print(f"Removed {self.cursor.rowcount} healed players from injury list!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def delete_retired_player(self):
        try:
            player_id = int(input("Player ID to retire: "))
            
            # First delete from related tables
            related_tables = [
                'PlayerMatchPerformance',
                'PlayerPositionsPlayed',
                'PlayerLanguageSpoken',
                'PlayerNationality',
                'Contracts',
                'InjuryRecord',
                'Captain',
                'YouthPlayer',
                'LoanPlayer'
            ]
            
            for table in related_tables:
                query = f"DELETE FROM {table} WHERE PlayerID = %s"
                self.cursor.execute(query, (player_id,))
            
            # Finally delete from Players table
            query = "DELETE FROM Players WHERE PlayerID = %s"
            self.cursor.execute(query, (player_id,))
            
            self.conn.commit()
            print("Player retired and removed successfully!")
        except pymysql.Error as err:
            print(f"Error: {err}")

    def delete_obsolete_tactics(self):
        try:
            # Delete tactics that aren't used in any matches
            query = """DELETE FROM Tactics 
                    WHERE TacticID NOT IN 
                    (SELECT TeamTacticID FROM ManagerMatchPerformance 
                    UNION 
                    SELECT OpponentTacticID FROM ManagerMatchPerformance)"""
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Deleted {self.cursor.rowcount} obsolete tactics!")
        except pymysql.Error as err:
            print(f"Error: {err}")  
    
    # Validation Functions
    def validate_formation(self, formation):
        # Basic formation validation (e.g., "4-4-2", "3-5-2")
        parts = formation.split('-')
        if len(parts) != 3:
            return False
        try:
            total = sum(int(p) for p in parts)
            return total == 10  # 10 outfield players
        except ValueError:
            return False
        
    # Main Menu
def final_extended_menu(self):
    while True:
        print("\nFootball Database Management System")
        print("=== Insert Operations ===")
        print("1. Insert Player")
        print("2. Create Team")
        print("3. Add Manager")
        print("4. Create Match")
        print("5. Setup Contract")
        print("6. Record Injury")
        print("7. Create Tactic")
        print("8. Add Youth Player")
        print("9. Add Player Language")
        print("10. Add Player Nationality")
        print("11. Register Captain")
        print("12. Register Loan Player")
        
        print("\n=== Update Operations ===")
        print("13. Update Player Stats")
        print("14. Update Contract")
        print("15. Update Tactics")
        print("16. Update Market Value")
        print("17. Update Team Budget")
        print("18. Update Player Position")
        print("19. Update Injury Status")
        print("20. Update League Standings")
        print("21. Promote Youth Player")
        
        print("\n=== Performance Recording ===")
        print("22. Record Manager Performance")
        print("23. Record Manager Achievement")
        
        print("\n=== Delete Operations ===")
        print("24. Delete Expired Contracts")
        print("25. Delete Completed Matches")
        print("26. Remove Healed Players")
        print("27. Delete Retired Player")
        print("28. Delete Obsolete Tactics")
        print("29. Exit")
        
        choice = input("Enter your choice (1-29): ")
        
        operations = {
            '1': self.insert_player,
            '2': self.create_team,
            '3': self.add_manager,
            '4': self.create_match,
            '5': self.setup_contract,
            '6': self.record_injury,
            '7': self.create_tactic,
            '8': self.add_youth_player,
            '9': self.add_player_language,
            '10': self.add_player_nationality,
            '11': self.register_captain,
            '12': self.register_loan_player,
            '13': self.update_player_stats,
            '14': self.update_contract,
            '15': self.update_tactics,
            '16': self.update_market_value,
            '17': self.update_team_budget,
            '18': self.update_player_position,
            '19': self.update_injury_status,
            '20': self.update_league_standings,
            '21': self.promote_youth_player,
            '22': self.record_manager_performance,
            '23': self.record_manager_achievement,
            '24': self.delete_expired_contracts,
            '25': self.delete_completed_matches,
            '26': self.remove_healed_players,
            '27': self.delete_retired_player,
            '28': self.delete_obsolete_tactics
        }
        
        if choice == '29':
            print("Goodbye!")
            self.conn.close()
            break
        elif choice in operations:
            operations[choice]()
        else:
            print("Invalid choice. Please try again.")
        

if __name__ == "__main__":
    db_system = FootballDatabaseSystem()
    db_system.final_extended_menu()