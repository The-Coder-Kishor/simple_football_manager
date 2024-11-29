# playernationality.py
import pymysql

def addRecord(con, cur):
    """
    Add a new player nationality record
    """
    try:
        # Show available players
        print("Available Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pn.Nationality) as CurrentNationalities
            FROM Players p
            LEFT JOIN PlayerNationality pn ON p.PlayerID = pn.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            nationalities = player['CurrentNationalities'] if player['CurrentNationalities'] else 'No nationalities'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Nationalities: {nationalities}")
        
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
        
        # Get nationality
        nationality = input("Enter Nationality: ").strip()
        while not nationality:
            print("Nationality cannot be empty.")
            nationality = input("Enter Nationality: ").strip()
        
        # Check if this nationality already exists for the player
        cur.execute("""
            SELECT * FROM PlayerNationality 
            WHERE PlayerID = %s AND Nationality = %s
        """, (player_id, nationality))
        
        if cur.fetchone():
            print("This nationality is already registered for this player.")
            return
        
        # SQL query to insert player nationality
        query = """
        INSERT INTO PlayerNationality 
        (PlayerID, Nationality) 
        VALUES (%s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, nationality))
        con.commit()
        
        print("Player nationality record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding player nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a player nationality record
    """
    try:
        # Show current player nationalities
        print("Current Player Nationalities:")
        cur.execute("""
            SELECT pn.PlayerNationalityID, p.PlayerName, pn.Nationality
            FROM PlayerNationality pn
            JOIN Players p ON pn.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pn.Nationality
        """)
        nationalities = cur.fetchall()
        
        for nationality in nationalities:
            print(f"ID: {nationality['PlayerNationalityID']}, "
                  f"Player: {nationality['PlayerName']}, "
                  f"Nationality: {nationality['Nationality']}")
        
        # Get nationality ID to delete
        while True:
            try:
                nationality_id = int(input("\nEnter Player Nationality ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # SQL query to delete player nationality
        query = "DELETE FROM PlayerNationality WHERE PlayerNationalityID = %s"
        
        # Execute the query
        cur.execute(query, (nationality_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Player nationality with ID {nationality_id} deleted successfully!")
        else:
            print(f"No nationality found with ID {nationality_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting player nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a player nationality record
    """
    try:
        # Show current player nationalities
        print("Current Player Nationalities:")
        cur.execute("""
            SELECT pn.PlayerNationalityID, p.PlayerName, pn.Nationality
            FROM PlayerNationality pn
            JOIN Players p ON pn.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pn.Nationality
        """)
        nationalities = cur.fetchall()
        
        for nationality in nationalities:
            print(f"ID: {nationality['PlayerNationalityID']}, "
                  f"Player: {nationality['PlayerName']}, "
                  f"Nationality: {nationality['Nationality']}")
        
        # Get nationality ID to update
        while True:
            try:
                nationality_id = int(input("\nEnter Player Nationality ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # Show available players
        print("\nAvailable Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pn.Nationality) as CurrentNationalities
            FROM Players p
            LEFT JOIN PlayerNationality pn ON p.PlayerID = pn.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            nationalities = player['CurrentNationalities'] if player['CurrentNationalities'] else 'No nationalities'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Nationalities: {nationalities}")
        
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
        
        # Get new nationality (optional)
        nationality = input("Enter new Nationality (press enter to skip): ").strip()
        
        # If both player ID and nationality are provided, check for duplicates
        if player_id and nationality:
            cur.execute("""
                SELECT * FROM PlayerNationality 
                WHERE PlayerID = %s AND Nationality = %s AND PlayerNationalityID != %s
            """, (player_id, nationality, nationality_id))
            
            if cur.fetchone():
                print("This nationality is already registered for this player.")
                return
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if player_id:
            update_fields.append("PlayerID = %s")
            params.append(player_id)
        if nationality:
            update_fields.append("Nationality = %s")
            params.append(nationality)
        
        if update_fields:
            # Add nationality ID to params
            params.append(nationality_id)
            
            query = f"UPDATE PlayerNationality SET {', '.join(update_fields)} WHERE PlayerNationalityID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Player nationality record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating player nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve player nationality records
    """
    try:
        # Option to retrieve all or specific player nationalities
        choice = input("Retrieve nationalities for (A)ll players or (S)pecific player? ").upper()
        
        if choice == 'A':
            # Retrieve all player nationalities
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pn.Nationality ORDER BY pn.Nationality) as Nationalities
            FROM Players p
            LEFT JOIN PlayerNationality pn ON p.PlayerID = pn.PlayerID
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
            
            # Retrieve specific player's nationalities
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pn.Nationality ORDER BY pn.Nationality) as Nationalities
            FROM Players p
            LEFT JOIN PlayerNationality pn ON p.PlayerID = pn.PlayerID
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
                print(f"Nationalities: {result['Nationalities'] if result['Nationalities'] else 'None registered'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving player nationality records: {e}")
    except ValueError:
        print("Please enter a valid Player ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")