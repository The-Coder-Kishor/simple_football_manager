# matchx.py
import pymysql
from datetime import datetime

def addRecord(con, cur):
    try:
        # Get match date
        while True:
            match_date = input("Enter Match Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(match_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Get goals with validation (allowing NULL for invalid/blank input)
        home_goals = None
        away_goals = None
        
        home_input = input("Enter Home Team Goals: ").strip()
        if home_input:
            try:
                home_goals = int(home_input)
                if home_goals < 0:
                    home_goals = None
                    print("Negative goals not allowed, setting to NULL.")
            except ValueError:
                print("Invalid input for home goals, setting to NULL.")

        away_input = input("Enter Away Team Goals: ").strip()
        if away_input:
            try:
                away_goals = int(away_input)
                if away_goals < 0:
                    away_goals = None
                    print("Negative goals not allowed, setting to NULL.")
            except ValueError:
                print("Invalid input for away goals, setting to NULL.")

        # Get attendees with validation
        while True:
            try:
                no_of_attendees = int(input("Enter Number of Attendees: "))
                if no_of_attendees >= 0:
                    break
                print("Attendees cannot be negative.")
            except ValueError:
                print("Please enter a valid number for attendees.")
        
        # Get team names
        home_team = input("Enter Home Club Name: ")
        away_team = input("Enter Away Club Name: ")
        
        # Get league details with year validation
        league_name = input("Enter League Name: ")
        while True:
            try:
                league_year = int(input("Enter League Year: "))
                if 1800 <= league_year <= 2100:
                    break
                print("Please enter a valid year between 1800 and 2100.")
            except ValueError:
                print("Please enter a valid year.")
        
        # Get stadium name
        stadium_name = input("Enter Stadium Name: ")
        
        # Verify all inputs exist in database
        try:
            cur.execute("SELECT ClubID FROM Clubs WHERE ClubName = %s", (home_team,))
            home_team_id = cur.fetchone()['ClubID']
            
            cur.execute("SELECT ClubID FROM Clubs WHERE ClubName = %s", (away_team,))
            away_team_id = cur.fetchone()['ClubID']
            
            cur.execute("SELECT LeagueID FROM Leagues WHERE LeagueName = %s AND LeagueYear = %s", 
                       (league_name, league_year))
            league_id = cur.fetchone()['LeagueID']
            
            cur.execute("SELECT StadiumID FROM Stadiums WHERE StadiumName = %s", (stadium_name,))
            stadium_id = cur.fetchone()['StadiumID']
        except:
            raise ValueError("One or more entered values do not exist in the database.")

        # Insert query
        query = """
        INSERT INTO MatchX 
        (Date, HomeGoals, AwayGoals, NoOfAttendees, HomeTeamID, AwayTeamID, LeagueID, StadiumID) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cur.execute(query, (match_date, home_goals, away_goals, no_of_attendees, 
                          home_team_id, away_team_id, league_id, stadium_id))
        con.commit()
        print("Match record added successfully!")
        
    except ValueError as ve:
        print(f"Error: {ve}")
    except pymysql.Error as e:
        con.rollback()
        print(f"Database Error: {e}")

def deleteRecord(con, cur):
    try:
        # Get match identifiers
        home_team = input("Enter Home Club Name of the match to delete: ")
        away_team = input("Enter Away Club Name of the match to delete: ")
        league_name = input("Enter League Name: ")
        while True:
            try:
                league_year = int(input("Enter League Year: "))
                if 1800 <= league_year <= 2100:
                    break
                print("Please enter a valid year between 1800 and 2100.")
            except ValueError:
                print("Please enter a valid year.")

        # First find and display the match to confirm
        query = """
        SELECT m.MatchID, m.Date, 
               h.ClubName as HomeTeam, m.HomeGoals,
               a.ClubName as AwayTeam, m.AwayGoals,
               l.LeagueName, l.LeagueYear,
               s.StadiumName,
               m.NoOfAttendees
        FROM MatchX m
        JOIN Clubs h ON m.HomeTeamID = h.ClubID
        JOIN Clubs a ON m.AwayTeamID = a.ClubID
        JOIN Leagues l ON m.LeagueID = l.LeagueID
        JOIN Stadiums s ON m.StadiumID = s.StadiumID
        WHERE h.ClubName = %s AND a.ClubName = %s 
        AND l.LeagueName = %s AND l.LeagueYear = %s
        """
        
        cur.execute(query, (home_team, away_team, league_name, league_year))
        match = cur.fetchone()
        
        if not match:
            print("No match found with the given details.")
            return

        # Display match details for confirmation
        print("\nMatch Details:")
        print(f"Date: {match['Date']}")
        print(f"Teams: {match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}")
        print(f"League: {match['LeagueName']} {match['LeagueYear']}")
        print(f"Stadium: {match['StadiumName']}")
        print(f"Attendance: {match['NoOfAttendees']}")

        # Confirm deletion
        confirm = input("\nAre you sure you want to delete this match? (yes/no): ").lower()
        
        if confirm == 'yes':
            delete_query = "DELETE FROM MatchX WHERE MatchID = %s"
            cur.execute(delete_query, (match['MatchID'],))
            con.commit()
            print("Match deleted successfully!")
        else:
            print("Deletion cancelled.")

    except pymysql.Error as e:
        con.rollback()
        print(f"Database Error: {e}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        con.rollback()
        print(f"Error: {e}")

def updateRecord(con, cur):
    try:
        # Get match identifiers
        home_team = input("Enter Home Club Name of the match to update: ")
        away_team = input("Enter Away Club Name of the match to update: ")
        league_name = input("Enter League Name: ")
        while True:
            try:
                league_year = int(input("Enter League Year: "))
                if 1800 <= league_year <= 2100:
                    break
                print("Please enter a valid year between 1800 and 2100.")
            except ValueError:
                print("Please enter a valid year.")

        # Find the match
        query = """
        SELECT m.* FROM MatchX m
        JOIN Clubs h ON m.HomeTeamID = h.ClubID
        JOIN Clubs a ON m.AwayTeamID = a.ClubID
        JOIN Leagues l ON m.LeagueID = l.LeagueID
        WHERE h.ClubName = %s AND a.ClubName = %s 
        AND l.LeagueName = %s AND l.LeagueYear = %s
        """
        cur.execute(query, (home_team, away_team, league_name, league_year))
        match = cur.fetchone()
        
        if not match:
            print("Match not found.")
            return

        # Get new values (empty input means no update)
        print("\nEnter new values (press Enter to skip):")
        
        # Date
        new_date = input("Enter new Match Date (YYYY-MM-DD): ")
        if new_date:
            try:
                datetime.strptime(new_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. This field will not be updated.")
                new_date = None

        # Goals
        new_home_goals = input("Enter new Home Team Goals: ")
        if new_home_goals:
            try:
                new_home_goals = int(new_home_goals)
                if new_home_goals < 0:
                    print("Goals cannot be negative. This field will not be updated.")
                    new_home_goals = None
            except ValueError:
                print("Invalid goals format. This field will not be updated.")
                new_home_goals = None

        new_away_goals = input("Enter new Away Team Goals: ")
        if new_away_goals:
            try:
                new_away_goals = int(new_away_goals)
                if new_away_goals < 0:
                    print("Goals cannot be negative. This field will not be updated.")
                    new_away_goals = None
            except ValueError:
                print("Invalid goals format. This field will not be updated.")
                new_away_goals = None

        # Attendees
        new_attendees = input("Enter new Number of Attendees: ")
        if new_attendees:
            try:
                new_attendees = int(new_attendees)
                if new_attendees < 0:
                    print("Attendees cannot be negative. This field will not be updated.")
                    new_attendees = None
            except ValueError:
                print("Invalid attendees format. This field will not be updated.")
                new_attendees = None

        # New teams
        new_home_team = input("Enter new Home Club Name (press Enter to skip): ")
        new_away_team = input("Enter new Away Club Name (press Enter to skip): ")

        # New league details
        new_league_name = input("Enter new League Name (press Enter to skip): ")
        new_league_year = input("Enter new League Year (press Enter to skip): ")
        if new_league_year:
            try:
                new_league_year = int(new_league_year)
                if not (1800 <= new_league_year <= 2100):
                    print("Invalid year. League year will not be updated.")
                    new_league_year = None
            except ValueError:
                print("Invalid year format. League year will not be updated.")
                new_league_year = None

        # New stadium
        new_stadium = input("Enter new Stadium Name (press Enter to skip): ")

        # Build update query dynamically
        update_parts = []
        params = []

        if new_date:
            update_parts.append("Date = %s")
            params.append(new_date)
        if new_home_goals is not None:
            update_parts.append("HomeGoals = %s")
            params.append(new_home_goals)
        if new_away_goals is not None:
            update_parts.append("AwayGoals = %s")
            params.append(new_away_goals)
        if new_attendees is not None:
            update_parts.append("NoOfAttendees = %s")
            params.append(new_attendees)

        # Handle team updates
        if new_home_team:
            try:
                cur.execute("SELECT ClubID FROM Clubs WHERE ClubName = %s", (new_home_team,))
                new_home_team_id = cur.fetchone()['ClubID']
                update_parts.append("HomeTeamID = %s")
                params.append(new_home_team_id)
            except:
                print("Invalid home team name. This field will not be updated.")

        if new_away_team:
            try:
                cur.execute("SELECT ClubID FROM Clubs WHERE ClubName = %s", (new_away_team,))
                new_away_team_id = cur.fetchone()['ClubID']
                update_parts.append("AwayTeamID = %s")
                params.append(new_away_team_id)
            except:
                print("Invalid away team name. This field will not be updated.")

        # Handle league update
        if new_league_name and new_league_year:
            try:
                cur.execute("SELECT LeagueID FROM Leagues WHERE LeagueName = %s AND LeagueYear = %s", 
                          (new_league_name, new_league_year))
                new_league_id = cur.fetchone()['LeagueID']
                update_parts.append("LeagueID = %s")
                params.append(new_league_id)
            except:
                print("Invalid league details. League will not be updated.")

        # Handle stadium update
        if new_stadium:
            try:
                cur.execute("SELECT StadiumID FROM Stadiums WHERE StadiumName = %s", (new_stadium,))
                new_stadium_id = cur.fetchone()['StadiumID']
                update_parts.append("StadiumID = %s")
                params.append(new_stadium_id)
            except:
                print("Invalid stadium name. Stadium will not be updated.")

        if update_parts:
            params.append(match['MatchID'])
            update_query = f"UPDATE MatchX SET {', '.join(update_parts)} WHERE MatchID = %s"
            cur.execute(update_query, params)
            con.commit()
            print("Match updated successfully!")
        else:
            print("No fields to update.")

    except pymysql.Error as e:
        con.rollback()
        print(f"Database Error: {e}")
    except Exception as e:
        con.rollback()
        print(f"Error: {e}")

def retrieveRecord(con, cur):
    try:
        print("\nRetrieval Options:")
        print("1. All Matches")
        print("2. Based on Club")
        print("3. Based on League name and Year")
        print("4. Based on Both (Club and League)")
        print("5. Based on Date")
        print("6. Average match attendance by club")
        
        while True:
            try:
                choice = int(input("\nEnter your choice (1-6): "))
                if 1 <= choice <= 6:
                    break
                print("Please enter a number between 1 and 6.")
            except ValueError:
                print("Please enter a valid number.")

        base_query = """
            SELECT m.MatchID, m.Date, 
                   h.ClubName as HomeTeam, m.HomeGoals,
                   a.ClubName as AwayTeam, m.AwayGoals,
                   l.LeagueName, l.LeagueYear,
                   s.StadiumName, s.City as StadiumCity,
                   m.NoOfAttendees
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            JOIN Stadiums s ON m.StadiumID = s.StadiumID
        """

        if choice == 1:
            # All matches
            query = base_query + " ORDER BY m.Date DESC"
            cur.execute(query)
            
        elif choice == 2:
            # Based on Club
            club_name = input("Enter Club Name: ")
            query = base_query + " WHERE h.ClubName = %s OR a.ClubName = %s ORDER BY m.Date DESC"
            cur.execute(query, (club_name, club_name))
            
        elif choice == 3:
            # Based on League
            league_name = input("Enter League Name: ")
            while True:
                try:
                    league_year = int(input("Enter League Year: "))
                    if 1800 <= league_year <= 2100:
                        break
                    print("Please enter a valid year between 1800 and 2100.")
                except ValueError:
                    print("Please enter a valid year.")

            query = base_query + " WHERE l.LeagueName = %s AND l.LeagueYear = %s ORDER BY m.Date DESC"
            cur.execute(query, (league_name, league_year))

        elif choice == 4:
            # Based on both Club and League
            club_name = input("Enter Club Name: ")
            league_name = input("Enter League Name: ")
            while True:
                try:
                    league_year = int(input("Enter League Year: "))
                    if 1800 <= league_year <= 2100:
                        break
                    print("Please enter a valid year between 1800 and 2100.")
                except ValueError:
                    print("Please enter a valid year.")

            query = base_query + """ 
                WHERE (h.ClubName = %s OR a.ClubName = %s)
                AND l.LeagueName = %s AND l.LeagueYear = %s 
                ORDER BY m.Date DESC
            """
            cur.execute(query, (club_name, club_name, league_name, league_year))

        elif choice == 5:
            # Based on Date
            while True:
                match_date = input("Enter Match Date (YYYY-MM-DD): ")
                try:
                    datetime.strptime(match_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Please enter a valid date in YYYY-MM-DD format.")
            
            query = base_query + " WHERE m.Date = %s ORDER BY m.Date DESC"
            cur.execute(query, (match_date,))
        elif choice == 6:
            # Retrieve average match attendance
            query = """
            SELECT AVG(m.noofattendees) as AverageAttendance
            FROM MatchX m
            """
            cur.execute(query)
            results = cur.fetchall()
            if not results or results[0]['AverageAttendance'] is None:
                print("No records found or no attendance data available.")
            else:
                print(f"Average Match Attendance: {results[0]['AverageAttendance']:.2f}")
            return
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("\nNo matches found.")
        else:
            print("\nMatch Results:")
            print("-" * 80)
            for match in results:
                print(f"Match ID: {match['MatchID']}")
                print(f"Date: {match['Date']}")
                print(f"Match: {match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}")
                print(f"League: {match['LeagueName']} {match['LeagueYear']}")
                print(f"Stadium: {match['StadiumName']} ({match['StadiumCity']})")
                print(f"Attendance: {match['NoOfAttendees']:,}")
                print("-" * 80)
            print(f"Total matches found: {len(results)}")

    except pymysql.Error as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")