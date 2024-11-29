# playermatchperformance.py
import pymysql

def addRecord(con, cur):
    """
    Add a new player match performance record
    """
    try:
        # Show available matches
        print("Recent Matches:")
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
            LIMIT 10
        """)
        matches = cur.fetchall()
        
        for match in matches:
            print(f"\nMatch ID: {match['MatchID']}, Date: {match['Date']}")
            print(f"{match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}")
            print(f"League: {match['LeagueName']}")
        
        # Get match ID
        while True:
            try:
                match_id = int(input("\nEnter Match ID: "))
                # Verify match exists
                cur.execute("SELECT MatchID FROM MatchX WHERE MatchID = %s", (match_id,))
                if cur.fetchone():
                    break
                print("Invalid Match ID.")
            except ValueError:
                print("Please enter a valid integer Match ID.")
        
        # Show available players for the teams involved in the match
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, c.ClubName
            FROM Players p
            JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE c.ClubID IN (
                SELECT HomeTeamID FROM MatchX WHERE MatchID = %s
                UNION
                SELECT AwayTeamID FROM MatchX WHERE MatchID = %s
            )
            ORDER BY c.ClubName, p.PlayerName
        """, (match_id, match_id))
        players = cur.fetchall()
        
        print("\nAvailable Players:")
        for player in players:
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}, Club: {player['ClubName']}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists and belongs to one of the teams
                if any(p['PlayerID'] == player_id for p in players):
                    break
                print("Invalid Player ID or player not from participating teams.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Check if performance record already exists
        cur.execute("""
            SELECT * FROM PlayerMatchPerformance 
            WHERE PlayerID = %s AND MatchID = %s
        """, (player_id, match_id))
        
        if cur.fetchone():
            print("Performance record already exists for this player in this match.")
            return
        
        # Get performance details
        # Pass accuracy validation (0-100%)
        while True:
            try:
                pass_accuracy = float(input("Enter Pass Accuracy (0-100): "))
                if 0 <= pass_accuracy <= 100:
                    break
                print("Pass accuracy must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for pass accuracy.")
        
        # Distance covered validation
        while True:
            try:
                distance_covered = float(input("Enter Distance Covered (in km): "))
                if distance_covered >= 0:
                    break
                print("Distance cannot be negative.")
            except ValueError:
                print("Please enter a valid number for distance covered.")
        
        # Minutes played validation
        while True:
            try:
                minutes_played = int(input("Enter Minutes Played (0-120): "))
                if 0 <= minutes_played <= 120:
                    break
                print("Minutes played must be between 0 and 120.")
            except ValueError:
                print("Please enter a valid integer for minutes played.")
        
        # Goals validation
        while True:
            try:
                goals = int(input("Enter Goals Scored: "))
                if goals >= 0:
                    break
                print("Goals cannot be negative.")
            except ValueError:
                print("Please enter a valid integer for goals.")
        
        # Assists validation
        while True:
            try:
                assists = int(input("Enter Assists: "))
                if assists >= 0:
                    break
                print("Assists cannot be negative.")
            except ValueError:
                print("Please enter a valid integer for assists.")
        
        # Rating validation (0-10)
        while True:
            try:
                rating = float(input("Enter Match Rating (0-10): "))
                if 0 <= rating <= 10:
                    break
                print("Rating must be between 0 and 10.")
            except ValueError:
                print("Please enter a valid number for rating.")
        
        # SQL query to insert performance record
        query = """
        INSERT INTO PlayerMatchPerformance 
        (PlayerID, MatchID, PassAccuracy, DistanceCovered, MinutesPlayed, 
         Goals, Assists, Ratings) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, match_id, pass_accuracy, distance_covered,
                          minutes_played, goals, assists, rating))
        con.commit()
        
        print("Player match performance record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a player match performance record
    """
    try:
        # Show recent performance records
        print("Recent Performance Records:")
        cur.execute("""
            SELECT pmp.PlayerID, pmp.MatchID, 
                   p.PlayerName, m.Date,
                   h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   pmp.Goals, pmp.Assists, pmp.Ratings
            FROM PlayerMatchPerformance pmp
            JOIN Players p ON pmp.PlayerID = p.PlayerID
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            ORDER BY m.Date DESC
            LIMIT 20
        """)
        performances = cur.fetchall()
        
        for perf in performances:
            print(f"\nPlayer: {perf['PlayerName']}")
            print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']} ({perf['Date']})")
            print(f"Stats: {perf['Goals']} goals, {perf['Assists']} assists, Rating: {perf['Ratings']}")
            print(f"Player ID: {perf['PlayerID']}, Match ID: {perf['MatchID']}")
        
        # Get player and match IDs
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                match_id = int(input("Enter Match ID: "))
                break
            except ValueError:
                print("Please enter valid integer IDs.")
        
        # SQL query to delete performance record
        query = """
        DELETE FROM PlayerMatchPerformance 
        WHERE PlayerID = %s AND MatchID = %s
        """
        
        # Execute the query
        cur.execute(query, (player_id, match_id))
        
        if cur.rowcount > 0:
            con.commit()
            print("Performance record deleted successfully!")
        else:
            print("No matching performance record found.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a player match performance record
    """
    try:
        # Show recent performance records
        print("Recent Performance Records:")
        cur.execute("""
            SELECT pmp.*, p.PlayerName, m.Date,
                   h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam
            FROM PlayerMatchPerformance pmp
            JOIN Players p ON pmp.PlayerID = p.PlayerID
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            ORDER BY m.Date DESC
            LIMIT 20
        """)
        performances = cur.fetchall()
        
        for perf in performances:
            print(f"\nPlayer: {perf['PlayerName']}")
            print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']} ({perf['Date']})")
            print(f"Stats: {perf['Goals']} goals, {perf['Assists']} assists")
            print(f"Pass Accuracy: {perf['PassAccuracy']}%, Distance: {perf['DistanceCovered']}km")
            print(f"Minutes: {perf['MinutesPlayed']}, Rating: {perf['Ratings']}")
            print(f"Player ID: {perf['PlayerID']}, Match ID: {perf['MatchID']}")
        
        # Get player and match IDs
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                match_id = int(input("Enter Match ID: "))
                # Verify record exists
                cur.execute("""
                    SELECT * FROM PlayerMatchPerformance 
                    WHERE PlayerID = %s AND MatchID = %s
                """, (player_id, match_id))
                if cur.fetchone():
                    break
                print("No performance record found for this player and match.")
            except ValueError:
                print("Please enter valid integer IDs.")
        
        # Get updated values (allow skipping)
        print("\nPress Enter to keep current values:")
        
        # Pass accuracy update
        pass_accuracy = input("Enter new Pass Accuracy (0-100): ")
        if pass_accuracy:
            pass_accuracy = float(pass_accuracy)
            if not (0 <= pass_accuracy <= 100):
                print("Invalid pass accuracy. Value not updated.")
                pass_accuracy = None
        
        # Distance covered update
        distance_covered = input("Enter new Distance Covered (km): ")
        if distance_covered:
            distance_covered = float(distance_covered)
            if distance_covered < 0:
                print("Invalid distance. Value not updated.")
                distance_covered = None
        
        # Minutes played update
        minutes_played = input("Enter new Minutes Played (0-120): ")
        if minutes_played:
            minutes_played = int(minutes_played)
            if not (0 <= minutes_played <= 120):
                print("Invalid minutes played. Value not updated.")
                minutes_played = None
        
        # Goals update
        goals = input("Enter new Goals Scored: ")
        if goals:
            goals = int(goals)
            if goals < 0:
                print("Invalid goals. Value not updated.")
                goals = None
        
        # Assists update
        assists = input("Enter new Assists: ")
        if assists:
            assists = int(assists)
            if assists < 0:
                print("Invalid assists. Value not updated.")
                assists = None
        
        # Rating update
        rating = input("Enter new Match Rating (0-10): ")
        if rating:
            rating = float(rating)
            if not (0 <= rating <= 10):
                print("Invalid rating. Value not updated.")
                rating = None
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if pass_accuracy is not None:
            update_fields.append("PassAccuracy = %s")
            params.append(pass_accuracy)
        if distance_covered is not None:
            update_fields.append("DistanceCovered = %s")
            params.append(distance_covered)
        if minutes_played is not None:
            update_fields.append("MinutesPlayed = %s")
            params.append(minutes_played)
        if goals is not None:
            update_fields.append("Goals = %s")
            params.append(goals)
        if assists is not None:
            update_fields.append("Assists = %s")
            params.append(assists)
        if rating is not None:
            update_fields.append("Ratings = %s")
            params.append(rating)
        
        if update_fields:
            # Add player and match IDs to params
            params.extend([player_id, match_id])
            
            query = f"""
            UPDATE PlayerMatchPerformance 
            SET {', '.join(update_fields)} 
            WHERE PlayerID = %s AND MatchID = %s
            """
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Performance record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve player match performance records
    """
    try:
        # Options for retrieval
        print("Retrieve performances by:")
        print("1. Player")
        print("2. Match")
        print("3. Top Performances")
        
        choice = input("Enter choice (1-3): ")
        
        if choice == '1':
            # Show players
            player_id = int(input("Enter Player ID: "))
            query = """
            SELECT pmp.*, p.PlayerName,
                   m.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName
            FROM PlayerMatchPerformance pmp
            JOIN Players p ON pmp.PlayerID = p.PlayerID
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            WHERE pmp.PlayerID = %s
            ORDER BY m.Date DESC
            """
            cur.execute(query, (player_id,))
            
        elif choice == '2':
            # Show match performances
            match_id = int(input("Enter Match ID: "))
            query = """
            SELECT pmp.*, p.PlayerName,
                   m.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName
            FROM PlayerMatchPerformance pmp
            JOIN Players p ON pmp.PlayerID = p.PlayerID
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            WHERE pmp.MatchID = %s
            ORDER BY pmp.Ratings DESC
            """
            cur.execute(query, (match_id,))
            
        elif choice == '3':
            # Show top performances
            print("\nFilter by:")
            print("1. Goals")
            print("2. Assists")
            print("3. Rating")
            
            filter_choice = input("Enter choice (1-3): ")
            
            if filter_choice == '1':
                order_by = "pmp.Goals DESC, pmp.Ratings DESC"
            elif filter_choice == '2':
                order_by = "pmp.Assists DESC, pmp.Ratings DESC"
            else:
                order_by = "pmp.Ratings DESC"
            
            query = f"""
            SELECT pmp.*, p.PlayerName,
                   m.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName
            FROM PlayerMatchPerformance pmp
            JOIN Players p ON pmp.PlayerID = p.PlayerID
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            ORDER BY {order_by}
            LIMIT 10
            """
            cur.execute(query)
        
        else:
            print("Invalid choice.")
            return
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No performance records found.")
        else:
            for perf in results:
                print("\nPerformance Details:")
                print(f"Player: {perf['PlayerName']}")
                print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']}")
                print(f"Date: {perf['Date']}")
                print(f"League: {perf['LeagueName']}")
                print(f"Goals: {perf['Goals']}")
                print(f"Assists: {perf['Assists']}")
                print(f"Pass Accuracy: {perf['PassAccuracy']}%")
                print(f"Distance Covered: {perf['DistanceCovered']}km")
                print(f"Minutes Played: {perf['MinutesPlayed']}")
                print(f"Rating: {perf['Ratings']}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving performance records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")