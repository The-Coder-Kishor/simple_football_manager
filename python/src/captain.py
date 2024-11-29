# captain.py
import pymysql

def addRecord(con, cur):
    """
    Add a new captain record
    """
    try:
        # Show available players who are not already captains
        print("Available Players (Not currently captains):")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, c.ClubName, 
                   p.OverallRating, p.Experience
            FROM Players p
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerID NOT IN (SELECT PlayerID FROM Captain)
            ORDER BY p.PlayerName
        """)
        players = cur.fetchall()
        
        if not players:
            print("No eligible players found for captain registration.")
            return
        
        for player in players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Club: {club}")
            print(f"Overall Rating: {player['OverallRating']}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists and is not already a captain
                cur.execute("""
                    SELECT PlayerID FROM Players 
                    WHERE PlayerID = %s 
                    AND PlayerID NOT IN (SELECT PlayerID FROM Captain)
                """, (player_id,))
                if cur.fetchone():
                    break
                print("Invalid Player ID or player is already registered as captain.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
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
        # Show current captains
        print("Current Captains:")
        cur.execute("""
            SELECT c.PlayerID, p.PlayerName, cl.ClubName,
                   c.CaptainWinningRate, c.CaptainBonus
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            ORDER BY p.PlayerName
        """)
        captains = cur.fetchall()
        
        for captain in captains:
            club = captain['ClubName'] if captain['ClubName'] else 'No Club'
            print(f"\nID: {captain['PlayerID']}, Name: {captain['PlayerName']}")
            print(f"Club: {club}")
            print(f"Winning Rate: {captain['CaptainWinningRate']}%")
            print(f"Bonus: ${captain['CaptainBonus']:,.2f}")
        
        # Get player ID to delete
        while True:
            try:
                player_id = int(input("\nEnter Player ID to remove from captaincy: "))
                break
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # SQL query to delete captain
        query = "DELETE FROM Captain WHERE PlayerID = %s"
        
        # Execute the query
        cur.execute(query, (player_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Captain with ID {player_id} removed successfully!")
        else:
            print(f"No captain found with ID {player_id}")
    
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
        # Show current captains
        print("Current Captains:")
        cur.execute("""
            SELECT c.PlayerID, p.PlayerName, cl.ClubName,
                   c.CaptainWinningRate, c.CaptainBonus
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            ORDER BY p.PlayerName
        """)
        captains = cur.fetchall()
        
        for captain in captains:
            club = captain['ClubName'] if captain['ClubName'] else 'No Club'
            print(f"\nID: {captain['PlayerID']}, Name: {captain['PlayerName']}")
            print(f"Club: {club}")
            print(f"Winning Rate: {captain['CaptainWinningRate']}%")
            print(f"Bonus: ${captain['CaptainBonus']:,.2f}")
        
        # Get player ID to update
        while True:
            try:
                player_id = int(input("\nEnter Player ID to update: "))
                # Verify captain exists
                cur.execute("SELECT * FROM Captain WHERE PlayerID = %s", (player_id,))
                if cur.fetchone():
                    break
                print("No captain found with this ID.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Get current record details
        cur.execute("""
            SELECT c.*, p.PlayerName 
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            WHERE c.PlayerID = %s
        """, (player_id,))
        current = cur.fetchone()
        
        print(f"\nUpdating captain record for {current['PlayerName']}")
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
            params.append(player_id)
            
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
        # Option to retrieve all or specific captain
        choice = input("Retrieve (A)ll captains or (S)pecific captain? ").upper()
        
        if choice == 'A':
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
                   p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            ORDER BY {order_by}
            """
            cur.execute(query)
        else:
            # Get specific player ID
            player_id = int(input("Enter Player ID: "))
            query = """
            SELECT c.*, p.PlayerName, p.OverallRating, cl.ClubName,
                   p.Experience
            FROM Captain c
            JOIN Players p ON c.PlayerID = p.PlayerID
            LEFT JOIN Clubs cl ON p.ClubID = cl.ClubID
            WHERE c.PlayerID = %s
            """
            cur.execute(query, (player_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No captains found.")
        else:
            for captain in results:
                print("\nCaptain Details:")
                print(f"Player ID: {captain['PlayerID']}")
                print(f"Name: {captain['PlayerName']}")
                print(f"Club: {captain['ClubName'] if captain['ClubName'] else 'No Club'}")
                print(f"Overall Rating: {captain['OverallRating']}")
                print(f"Experience: {captain['Experience']} years")
                print(f"Winning Rate: {captain['CaptainWinningRate']}%")
                print(f"Captain Bonus: ${captain['CaptainBonus']:,.2f}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving captain records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")