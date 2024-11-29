# captain.py
import pymysql

def addRecord(con, cur):
    """
    Add a new captain record
    """
    try:
        # Get player name
        while True:
            player_name = input("\nEnter Player Name: ")
            # Verify player exists and is not already a captain
            cur.execute("""
                SELECT PlayerID FROM Players 
                WHERE PlayerName = %s 
                AND PlayerID NOT IN (SELECT PlayerID FROM Captain)
            """, (player_name,))
            player = cur.fetchone()
            if player:
                player_id = player['PlayerID']
                break
            print("Invalid Player Name or player is already registered as captain.")
        
        # Winning rate validation (0-100%)
        while True:
            try:
                winning_rate = float(input("Enter Captain Winning Rate (0-100): "))
                if 0 <= winning_rate <= 100:
                    break
                print("Winning rate must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for winning rate.")
        
        # Captain bonus validation
        while True:
            try:
                captain_bonus = float(input("Enter Captain Bonus Amount: "))
                if captain_bonus >= 0:
                    break
                print("Bonus amount cannot be negative.")
            except ValueError:
                print("Please enter a valid number for bonus amount.")
        
        # SQL query to insert captain
        query = """
        INSERT INTO Captain 
        (PlayerID, CaptainWinningRate, CaptainBonus) 
        VALUES (%s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, winning_rate, captain_bonus))
        con.commit()
        
        print("Captain record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding captain record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a captain record
    """
    try:
        # Get player name to delete
        player_name = input("\nEnter Player Name to remove from captaincy: ")
        
        # Get PlayerID from name
        cur.execute("""
            SELECT PlayerID FROM Players 
            WHERE PlayerName = %s
        """, (player_name,))
        player = cur.fetchone()
        
        if not player:
            print("Player not found.")
            return
        
        # SQL query to delete captain
        query = "DELETE FROM Captain WHERE PlayerID = %s"
        
        # Execute the query
        cur.execute(query, (player['PlayerID'],))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Captain {player_name} removed successfully!")
        else:
            print(f"No captain found with name {player_name}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting captain record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a captain record
    """
    try:
        # Get player name to update
        while True:
            player_name = input("\nEnter Player Name to update: ")
            # Get PlayerID from name
            cur.execute("""
                SELECT p.PlayerID, c.* 
                FROM Players p
                JOIN Captain c ON p.PlayerID = c.PlayerID
                WHERE p.PlayerName = %s
            """, (player_name,))
            current = cur.fetchone()
            if current:
                break
            print("No captain found with this name.")
        
        print(f"\nUpdating captain record for {player_name}")
        print("Press Enter to keep current values:")
        
        # Winning rate update
        winning_rate = input(f"Enter new Winning Rate (current: {current['CaptainWinningRate']}%): ")
        if winning_rate:
            try:
                winning_rate = float(winning_rate)
                if not (0 <= winning_rate <= 100):
                    print("Winning rate must be between 0 and 100. Value not updated.")
                    winning_rate = None
            except ValueError:
                print("Invalid winning rate. Value not updated.")
                winning_rate = None
        
        # Captain bonus update
        bonus = input(f"Enter new Captain Bonus (current: ${current['CaptainBonus']:,.2f}): ")
        if bonus:
            try:
                bonus = float(bonus)
                if bonus < 0:
                    print("Bonus cannot be negative. Value not updated.")
                    bonus = None
            except ValueError:
                print("Invalid bonus amount. Value not updated.")
                bonus = None
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if winning_rate is not None:
            update_fields.append("CaptainWinningRate = %s")
            params.append(winning_rate)
        if bonus is not None:
            update_fields.append("CaptainBonus = %s")
            params.append(bonus)
        
        if update_fields:
            # Add player ID to params
            params.append(current['PlayerID'])
            
            query = f"UPDATE Captain SET {', '.join(update_fields)} WHERE PlayerID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Captain record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating captain record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve captain records
    """
    try:
        print("\nRetrieval Options:")
        print("1. All Captains")
        print("2. Search by Player Name")
        print("3. Search by Club")
        print("4. Search by League")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            # Option to sort by winning rate or bonus
            sort_choice = input("Sort by (W)inning rate or (B)onus? ").upper()
            
            if sort_choice == 'W':
                order_by = "c.CaptainWinningRate DESC"
            elif sort_choice == 'B':
                order_by = "c.CaptainBonus DESC"
            else:
                order_by = "p.PlayerName"
            
            query = f"""
            SELECT c.*, p.PlayerName, p.OverallRating, cl.ClubName,
                   l.LeagueName, p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            LEFT JOIN PlaysIn pi ON pi.ClubID = cl.ClubID
            LEFT JOIN Leagues l ON pi.LeagueID = l.LeagueID
            ORDER BY {order_by}
            """
            cur.execute(query)
            
        elif choice == '2':
            player_name = input("Enter Player Name (or part of name): ")
            query = """
            SELECT c.*, p.PlayerName, p.OverallRating, cl.ClubName,
                   l.LeagueName, p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            LEFT JOIN PlaysIn pi ON pi.ClubID = cl.ClubID
            LEFT JOIN Leagues l ON pi.LeagueID = l.LeagueID
            WHERE p.PlayerName LIKE %s
            """
            cur.execute(query, (f'%{player_name}%',))
            
        elif choice == '3':
            club_name = input("\nEnter Club Name: ")
            query = """
            SELECT c.*, p.PlayerName, p.OverallRating, cl.ClubName,
                   l.LeagueName, p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            LEFT JOIN PlaysIn pi ON pi.ClubID = cl.ClubID
            LEFT JOIN Leagues l ON pi.LeagueID = l.LeagueID
            WHERE cl.ClubName LIKE %s
            """
            cur.execute(query, (f'%{club_name}%',))
            
        elif choice == '4':
            # Show available leagues
            cur.execute("SELECT DISTINCT LeagueName FROM Leagues ORDER BY LeagueName")
            leagues = cur.fetchall()
            print("\nAvailable Leagues:")
            for league in leagues:
                print(league['LeagueName'])
            
            league_name = input("\nEnter League Name: ")
            query = """
            SELECT c.*, p.PlayerName, p.OverallRating, cl.ClubName,
                   l.LeagueName, p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            LEFT JOIN PlaysIn pi ON pi.ClubID = cl.ClubID
            LEFT JOIN Leagues l ON pi.LeagueID = l.LeagueID
            WHERE l.LeagueName LIKE %s
            """
            cur.execute(query, (f'%{league_name}%',))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No captains found.")
        else:
            for captain in results:
                print("\nCaptain Details:")
                print(f"Name: {captain['PlayerName']}")
                print(f"Club: {captain['ClubName'] if captain['ClubName'] else 'No Club'}")
                print(f"League: {captain['LeagueName'] if captain['LeagueName'] else 'No League'}")
                print(f"Overall Rating: {captain['OverallRating']}")
                print(f"Experience: {captain['Experience']} years")
                print(f"Winning Rate: {captain['CaptainWinningRate']}%")
                print(f"Captain Bonus: ${captain['CaptainBonus']:,.2f}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving captain records: {e}")
    except ValueError:
        print("Please enter valid values.")
    except Exception as e:
        print(f"Unexpected error: {e}")