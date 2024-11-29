# playerpositionsplayed.py
import pymysql

def addRecord(con, cur):
    """
    Add a new player position record
    """
    try:
        # Show available players with their current positions
        print("Available Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pp.Position) as CurrentPositions
            FROM Players p
            LEFT JOIN PlayerPositionsPlayed pp ON p.PlayerID = pp.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            positions = player['CurrentPositions'] if player['CurrentPositions'] else 'No positions registered'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Positions: {positions}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists
                cur.execute("SELECT PlayerID FROM Players WHERE PlayerID = %s", (player_id,))
                if cur.fetchone():
                    break
                print("Player ID not found. Please enter a valid ID.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Show standard football positions
        print("\nStandard Football Positions:")
        positions = [
            "GK (Goalkeeper)", 
            "CB (Center Back)", "RB (Right Back)", "LB (Left Back)", 
            "CDM (Defensive Midfielder)", "CM (Central Midfielder)", "CAM (Attacking Midfielder)",
            "RM (Right Midfielder)", "LM (Left Midfielder)",
            "RW (Right Wing)", "LW (Left Wing)",
            "ST (Striker)", "CF (Center Forward)"
        ]
        for pos in positions:
            print(pos)
        
        # Get position
        position = input("\nEnter Position (e.g., GK, CB, ST): ").strip().upper()
        while not position:
            print("Position cannot be empty.")
            position = input("Enter Position: ").strip().upper()
        
        # Check if this position is already registered for the player
        cur.execute("""
            SELECT * FROM PlayerPositionsPlayed 
            WHERE PlayerID = %s AND Position = %s
        """, (player_id, position))
        
        if cur.fetchone():
            print("This position is already registered for this player.")
            return
        
        # SQL query to insert player position
        query = """
        INSERT INTO PlayerPositionsPlayed 
        (PlayerID, Position) 
        VALUES (%s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, position))
        con.commit()
        
        print("Player position record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding player position record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a player position record
    """
    try:
        # Show current player positions
        print("Current Player Positions:")
        cur.execute("""
            SELECT pp.PlayerPositionID, p.PlayerName, pp.Position
            FROM PlayerPositionsPlayed pp
            JOIN Players p ON pp.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pp.Position
        """)
        positions = cur.fetchall()
        
        for position in positions:
            print(f"ID: {position['PlayerPositionID']}, "
                  f"Player: {position['PlayerName']}, "
                  f"Position: {position['Position']}")
        
        # Get position ID to delete
        while True:
            try:
                position_id = int(input("\nEnter Player Position ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # SQL query to delete player position
        query = "DELETE FROM PlayerPositionsPlayed WHERE PlayerPositionID = %s"
        
        # Execute the query
        cur.execute(query, (position_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Player position with ID {position_id} deleted successfully!")
        else:
            print(f"No position record found with ID {position_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting player position record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a player position record
    """
    try:
        # Show current player positions
        print("Current Player Positions:")
        cur.execute("""
            SELECT pp.PlayerPositionID, p.PlayerName, pp.Position
            FROM PlayerPositionsPlayed pp
            JOIN Players p ON pp.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pp.Position
        """)
        positions = cur.fetchall()
        
        for position in positions:
            print(f"ID: {position['PlayerPositionID']}, "
                  f"Player: {position['PlayerName']}, "
                  f"Position: {position['Position']}")
        
        # Get position ID to update
        while True:
            try:
                position_id = int(input("\nEnter Player Position ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # Show available players
        print("\nAvailable Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pp.Position) as CurrentPositions
            FROM Players p
            LEFT JOIN PlayerPositionsPlayed pp ON p.PlayerID = pp.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            positions = player['CurrentPositions'] if player['CurrentPositions'] else 'No positions registered'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Positions: {positions}")
        
        # Get new player ID (optional)
        player_id = input("\nEnter new Player ID (press enter to skip): ")
        if player_id:
            try:
                player_id = int(player_id)
                # Verify player exists
                cur.execute("SELECT PlayerID FROM Players WHERE PlayerID = %s", (player_id,))
                if not cur.fetchone():
                    print("Player ID not found. Player not updated.")
                    player_id = None
            except ValueError:
                print("Invalid player ID. Player not updated.")
                player_id = None
        
        # Show standard football positions
        print("\nStandard Football Positions:")
        positions = [
            "GK (Goalkeeper)", 
            "CB (Center Back)", "RB (Right Back)", "LB (Left Back)", 
            "CDM (Defensive Midfielder)", "CM (Central Midfielder)", "CAM (Attacking Midfielder)",
            "RM (Right Midfielder)", "LM (Left Midfielder)",
            "RW (Right Wing)", "LW (Left Wing)",
            "ST (Striker)", "CF (Center Forward)"
        ]
        for pos in positions:
            print(pos)
        
        # Get new position (optional)
        position = input("\nEnter new Position (press enter to skip): ").strip()
        if position:
            position = position.upper()
        
        # If both player ID and position are provided, check for duplicates
        if player_id and position:
            cur.execute("""
                SELECT * FROM PlayerPositionsPlayed 
                WHERE PlayerID = %s AND Position = %s AND PlayerPositionID != %s
            """, (player_id, position, position_id))
            
            if cur.fetchone():
                print("This position is already registered for this player.")
                return
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if player_id:
            update_fields.append("PlayerID = %s")
            params.append(player_id)
        if position:
            update_fields.append("Position = %s")
            params.append(position)
        
        if update_fields:
            # Add position ID to params
            params.append(position_id)
            
            query = f"UPDATE PlayerPositionsPlayed SET {', '.join(update_fields)} WHERE PlayerPositionID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Player position record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating player position record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve player position records
    """
    try:
        # Option to retrieve all or specific player positions
        choice = input("Retrieve positions for (A)ll players or (S)pecific player? ").upper()
        
        if choice == 'A':
            # Retrieve all player positions
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pp.Position ORDER BY pp.Position) as Positions
            FROM Players p
            LEFT JOIN PlayerPositionsPlayed pp ON p.PlayerID = pp.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
            ORDER BY p.PlayerName
            """
            cur.execute(query)
        else:
            # Get player ID
            while True:
                try:
                    player_id = int(input("Enter Player ID: "))
                    break
                except ValueError:
                    print("Please enter a valid integer Player ID.")
            
            # Retrieve specific player's positions
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pp.Position ORDER BY pp.Position) as Positions
            FROM Players p
            LEFT JOIN PlayerPositionsPlayed pp ON p.PlayerID = pp.PlayerID
            WHERE p.PlayerID = %s
            GROUP BY p.PlayerID, p.PlayerName
            """
            cur.execute(query, (player_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No players found.")
        else:
            for result in results:
                print("\nPlayer Details:")
                print(f"Player ID: {result['PlayerID']}")
                print(f"Name: {result['PlayerName']}")
                print(f"Positions: {result['Positions'] if result['Positions'] else 'None registered'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving player position records: {e}")
    except ValueError:
        print("Please enter a valid Player ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")