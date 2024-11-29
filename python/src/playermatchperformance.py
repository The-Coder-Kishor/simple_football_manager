# playermatchperformance.py
import pymysql

def addRecord(con, cur):
    """
    Add a new player match performance record
    """
    try:
        # Get match ID
        match_id = int(input("\nEnter Match ID: "))
        
        # Show available players for the teams involved in the match
        cur.execute("""
            SELECT p.PlayerName, c.ClubName
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
            print(f"Name: {player['PlayerName']}, Club: {player['ClubName']}")
        
        # Get player name
        player_name = input("\nEnter Player Name: ")
        
        # Get player ID from name
        cur.execute("SELECT PlayerID FROM Players WHERE PlayerName = %s", (player_name,))
        player_result = cur.fetchone()
        if not player_result:
            print("Player not found.")
            return
        player_id = player_result['PlayerID']
        
        # Get performance details
        pass_accuracy = float(input("Enter Pass Accuracy (0-100): "))
        distance_covered = float(input("Enter Distance Covered (in km): "))
        minutes_played = int(input("Enter Minutes Played (0-120): "))
        goals = int(input("Enter Goals Scored: "))
        assists = int(input("Enter Assists: "))
        rating = float(input("Enter Match Rating (0-10): "))
        
        # Insert performance record
        query = """
        INSERT INTO PlayerMatchPerformance 
        (PlayerID, MatchID, PassAccuracy, DistanceCovered, MinutesPlayed, 
         Goals, Assists, Ratings) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
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
        player_name = input("\nEnter Player Name: ")
        match_id = int(input("Enter Match ID: "))
        
        # Get player ID from name
        cur.execute("SELECT PlayerID FROM Players WHERE PlayerName = %s", (player_name,))
        player_result = cur.fetchone()
        if not player_result:
            print("Player not found.")
            return
        player_id = player_result['PlayerID']
        
        # Delete the record
        cur.execute("""
            DELETE FROM PlayerMatchPerformance 
            WHERE PlayerID = %s AND MatchID = %s
        """, (player_id, match_id))
        
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
        player_name = input("\nEnter Player Name: ")
        match_id = int(input("Enter Match ID: "))
        
        # Get player ID from name
        cur.execute("SELECT PlayerID FROM Players WHERE PlayerName = %s", (player_name,))
        player_result = cur.fetchone()
        if not player_result:
            print("Player not found.")
            return
        player_id = player_result['PlayerID']
        
        # Verify record exists
        cur.execute("""
            SELECT * FROM PlayerMatchPerformance 
            WHERE PlayerID = %s AND MatchID = %s
        """, (player_id, match_id))
        if not cur.fetchone():
            print("No performance record found for this player and match.")
            return
        
        # Get updated values (allow skipping)
        print("\nPress Enter to keep current values:")
        
        # Pass accuracy update
        pass_accuracy = input("Enter new Pass Accuracy (0-100): ")
        if pass_accuracy:
            pass_accuracy = float(pass_accuracy)
        
        # Distance covered update
        distance_covered = input("Enter new Distance Covered (km): ")
        if distance_covered:
            distance_covered = float(distance_covered)
        
        # Minutes played update
        minutes_played = input("Enter new Minutes Played (0-120): ")
        if minutes_played:
            minutes_played = int(minutes_played)
        
        # Goals update
        goals = input("Enter new Goals Scored: ")
        if goals:
            goals = int(goals)
        
        # Assists update
        assists = input("Enter new Assists: ")
        if assists:
            assists = int(assists)
        
        # Rating update
        rating = input("Enter new Match Rating (0-10): ")
        if rating:
            rating = float(rating)
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if pass_accuracy:
            update_fields.append("PassAccuracy = %s")
            params.append(pass_accuracy)
        if distance_covered:
            update_fields.append("DistanceCovered = %s")
            params.append(distance_covered)
        if minutes_played:
            update_fields.append("MinutesPlayed = %s")
            params.append(minutes_played)
        if goals:
            update_fields.append("Goals = %s")
            params.append(goals)
        if assists:
            update_fields.append("Assists = %s")
            params.append(assists)
        if rating:
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
        print("4. Player Performance History")
        
        choice = input("Enter choice (1-4): ")
        
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
        elif choice == '4':
            import numpy as np
            from scipy.stats import linregress
            from datetime import datetime

            # Ask for player ID
            player_id = int(input("Enter Player ID to calculate development: "))

            # Retrieve all ratings of the specified player
            query = """
            SELECT pmp.Ratings, m.Date
            FROM PlayerMatchPerformance pmp
            JOIN MatchX m ON pmp.MatchID = m.MatchID
            WHERE pmp.PlayerID = %s
            ORDER BY m.Date
            """
            cur.execute(query, (player_id,))
            results = cur.fetchall()

            if not results:
                print("No performance records found for the specified player.")
            else:
                # Extract dates and ratings
                dates = [result['Date'] for result in results]
                ratings = [result['Rating'] for result in results]

                # Convert dates to ordinal format for linear fitting
                dates_ordinal = [datetime.strptime(date, '%Y-%m-%d').toordinal() for date in dates]

                # Perform linear fitting
                slope, intercept, r_value, p_value, std_err = linregress(dates_ordinal, ratings)

                # Display the results
                print(f"Player development (linear fitting):")
                print(f"Slope (rate of change): {slope}")
                print(f"Intercept: {intercept}")
                print(f"R-squared: {r_value**2}")
                print(f"P-value: {p_value}")
                print(f"Standard error: {std_err}")    
        
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