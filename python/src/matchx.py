# matchx.py
import pymysql
from datetime import datetime

def addRecord(con, cur):
    """
    Add a new match record
    """
    try:
        # Match date validation
        while True:
            match_date = input("Enter Match Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(match_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Goals validation
        while True:
            try:
                home_goals = int(input("Enter Home Team Goals: "))
                if home_goals >= 0:
                    break
                print("Goals cannot be negative.")
            except ValueError:
                print("Please enter a valid integer for goals.")
        
        while True:
            try:
                away_goals = int(input("Enter Away Team Goals: "))
                if away_goals >= 0:
                    break
                print("Goals cannot be negative.")
            except ValueError:
                print("Please enter a valid integer for goals.")
        
        # Attendees validation
        while True:
            try:
                no_of_attendees = int(input("Enter Number of Attendees: "))
                if no_of_attendees >= 0:
                    break
                print("Number of attendees cannot be negative.")
            except ValueError:
                print("Please enter a valid integer for attendees.")
        
        # Show available clubs for home and away team selection
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
        
        # Get home and away team IDs
        while True:
            try:
                home_team_id = int(input("Enter Home Team ID: "))
                away_team_id = int(input("Enter Away Team ID: "))
                if home_team_id != away_team_id:
                    break
                print("Home and away team cannot be the same.")
            except ValueError:
                print("Please enter valid integer IDs.")
        
        # Show available leagues
        print("\nAvailable Leagues:")
        cur.execute("SELECT LeagueID, LeagueName, LeagueYear FROM Leagues")
        leagues = cur.fetchall()
        for league in leagues:
            print(f"ID: {league['LeagueID']}, Name: {league['LeagueName']}, Year: {league['LeagueYear']}")
        
        # Get league ID
        while True:
            try:
                league_id = int(input("Enter League ID: "))
                break
            except ValueError:
                print("Please enter a valid integer League ID.")
        
        # Show available stadiums
        print("\nAvailable Stadiums:")
        cur.execute("SELECT StadiumID, StadiumName, City FROM Stadiums")
        stadiums = cur.fetchall()
        for stadium in stadiums:
            print(f"ID: {stadium['StadiumID']}, Name: {stadium['StadiumName']}, City: {stadium['City']}")
        
        # Get stadium ID
        while True:
            try:
                stadium_id = int(input("Enter Stadium ID: "))
                break
            except ValueError:
                print("Please enter a valid integer Stadium ID.")
        
        # SQL query to insert match
        query = """
        INSERT INTO MatchX 
        (Date, HomeGoals, AwayGoals, NoOfAttendees, HomeTeamID, AwayTeamID, LeagueID, StadiumID) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (match_date, home_goals, away_goals, no_of_attendees, 
                          home_team_id, away_team_id, league_id, stadium_id))
        con.commit()
        
        print("Match record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding match record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a match record
    """
    try:
        # Retrieve and display matches to help user choose
        print("Current Matches:")
        cur.execute("""
            SELECT m.MatchID, m.Date, 
                   h.ClubName as HomeTeam, m.HomeGoals,
                   a.ClubName as AwayTeam, m.AwayGoals,
                   l.LeagueName
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            ORDER BY m.Date DESC
        """)
        matches = cur.fetchall()
        
        for match in matches:
            print(f"ID: {match['MatchID']}, Date: {match['Date']}, "
                  f"{match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}, "
                  f"League: {match['LeagueName']}")
        
        # Get match ID to delete
        while True:
            try:
                match_id = int(input("Enter Match ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer Match ID.")
        
        # SQL query to delete match
        query = "DELETE FROM MatchX WHERE MatchID = %s"
        
        # Execute the query
        cur.execute(query, (match_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Match with ID {match_id} deleted successfully!")
        else:
            print(f"No match found with ID {match_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting match record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a match record
    """
    try:
        # Retrieve and display matches to help user choose
        print("Current Matches:")
        cur.execute("""
            SELECT m.MatchID, m.Date, 
                   h.ClubName as HomeTeam, m.HomeGoals,
                   a.ClubName as AwayTeam, m.AwayGoals,
                   l.LeagueName
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            ORDER BY m.Date DESC
        """)
        matches = cur.fetchall()
        
        for match in matches:
            print(f"ID: {match['MatchID']}, Date: {match['Date']}, "
                  f"{match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}, "
                  f"League: {match['LeagueName']}")
        
        # Get match ID to update
        while True:
            try:
                match_id = int(input("Enter Match ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer Match ID.")
        
        # Collect new details (allow skipping)
        match_date = input("Enter new Match Date (YYYY-MM-DD) (press enter to skip): ")
        if match_date:
            while True:
                try:
                    datetime.strptime(match_date, '%Y-%m-%d')
                    break
                except ValueError:
                    match_date = input("Please enter a valid date in YYYY-MM-DD format: ")
        
        home_goals = input("Enter new Home Team Goals (press enter to skip): ")
        if home_goals:
            while True:
                try:
                    home_goals = int(home_goals)
                    if home_goals >= 0:
                        break
                    home_goals = input("Goals cannot be negative: ")
                except ValueError:
                    home_goals = input("Please enter a valid integer for goals: ")
        
        away_goals = input("Enter new Away Team Goals (press enter to skip): ")
        if away_goals:
            while True:
                try:
                    away_goals = int(away_goals)
                    if away_goals >= 0:
                        break
                    away_goals = input("Goals cannot be negative: ")
                except ValueError:
                    away_goals = input("Please enter a valid integer for goals: ")
        
        no_of_attendees = input("Enter new Number of Attendees (press enter to skip): ")
        if no_of_attendees:
            while True:
                try:
                    no_of_attendees = int(no_of_attendees)
                    if no_of_attendees >= 0:
                        break
                    no_of_attendees = input("Number of attendees cannot be negative: ")
                except ValueError:
                    no_of_attendees = input("Please enter a valid integer for attendees: ")
        
        # Show available related records
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
        
        home_team_id = input("Enter new Home Team ID (press enter to skip): ")
        away_team_id = input("Enter new Away Team ID (press enter to skip): ")
        
        if home_team_id and away_team_id:
            if home_team_id == away_team_id:
                print("Home and away team cannot be the same. Teams not updated.")
                home_team_id = away_team_id = None
        
        print("\nAvailable Leagues:")
        cur.execute("SELECT LeagueID, LeagueName, LeagueYear FROM Leagues")
        leagues = cur.fetchall()
        for league in leagues:
            print(f"ID: {league['LeagueID']}, Name: {league['LeagueName']}, Year: {league['LeagueYear']}")
        
        league_id = input("Enter new League ID (press enter to skip): ")
        
        print("\nAvailable Stadiums:")
        cur.execute("SELECT StadiumID, StadiumName, City FROM Stadiums")
        stadiums = cur.fetchall()
        for stadium in stadiums:
            print(f"ID: {stadium['StadiumID']}, Name: {stadium['StadiumName']}, City: {stadium['City']}")
        
        stadium_id = input("Enter new Stadium ID (press enter to skip): ")
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if match_date:
            update_fields.append("Date = %s")
            params.append(match_date)
        if home_goals is not None:
            update_fields.append("HomeGoals = %s")
            params.append(home_goals)
        if away_goals is not None:
            update_fields.append("AwayGoals = %s")
            params.append(away_goals)
        if no_of_attendees is not None:
            update_fields.append("NoOfAttendees = %s")
            params.append(no_of_attendees)
        if home_team_id:
            update_fields.append("HomeTeamID = %s")
            params.append(int(home_team_id))
        if away_team_id:
            update_fields.append("AwayTeamID = %s")
            params.append(int(away_team_id))
        if league_id:
            update_fields.append("LeagueID = %s")
            params.append(int(league_id))
        if stadium_id:
            update_fields.append("StadiumID = %s")
            params.append(int(stadium_id))
        
        # Add match ID to params
        params.append(match_id)
        
        if update_fields:
            query = f"UPDATE MatchX SET {', '.join(update_fields)} WHERE MatchID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Match record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating match record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve match records
    """
    try:
        # Option to retrieve all or specific match
        choice = input("Retrieve (A)ll or (S)pecific match? ").upper()
        
        if choice == 'A':
            # Retrieve all matches with related information
            query = """
            SELECT m.*,
                   h.ClubName as HomeTeamName,
                   a.ClubName as AwayTeamName,
                   l.LeagueName,
                   s.StadiumName,
                   s.City as StadiumCity
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            JOIN Stadiums s ON m.StadiumID = s.StadiumID
            ORDER BY m.Date DESC
            """
            cur.execute(query)
        else:
            # Retrieve specific match
            match_id = int(input("Enter Match ID: "))
            query = """
            SELECT m.*,
                   h.ClubName as HomeTeamName,
                   a.ClubName as AwayTeamName,
                   l.LeagueName,
                   s.StadiumName,
                   s.City as StadiumCity
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            JOIN Stadiums s ON m.StadiumID = s.StadiumID
            WHERE m.MatchID = %s
            """
            cur.execute(query, (match_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No matches found.")
        else:
            for match in results:
                print("\nMatch Details:")
                print(f"Match ID: {match['MatchID']}")
                print(f"Date: {match['Date']}")
                print(f"Score: {match['HomeTeamName']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeamName']}")
                print(f"League: {match['LeagueName']}")
                print(f"Stadium: {match['StadiumName']} ({match['StadiumCity']})")
                print(f"Attendance: {match['NoOfAttendees']:,}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving match records: {e}")
    except ValueError:
        print("Please enter a valid Match ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")