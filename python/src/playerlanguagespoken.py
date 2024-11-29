# playerlanguagespoken.py
import pymysql

def addRecord(con, cur):
    """
    Add a new player language record
    """
    try:
        # Show available players with their current languages
        print("Available Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pl.Language) as CurrentLanguages
            FROM Players p
            LEFT JOIN PlayerLanguageSpoken pl ON p.PlayerID = pl.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            languages = player['CurrentLanguages'] if player['CurrentLanguages'] else 'No languages registered'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Languages: {languages}")
        
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
        
        # Get language
        language = input("Enter Language: ").strip().capitalize()
        while not language:
            print("Language cannot be empty.")
            language = input("Enter Language: ").strip().capitalize()
        
        # Check if this language is already registered for the player
        cur.execute("""
            SELECT * FROM PlayerLanguageSpoken 
            WHERE PlayerID = %s AND Language = %s
        """, (player_id, language))
        
        if cur.fetchone():
            print("This language is already registered for this player.")
            return
        
        # SQL query to insert player language
        query = """
        INSERT INTO PlayerLanguageSpoken 
        (PlayerID, Language) 
        VALUES (%s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, language))
        con.commit()
        
        print("Player language record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding player language record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a player language record
    """
    try:
        # Show current player languages
        print("Current Player Languages:")
        cur.execute("""
            SELECT pl.PlayerLanguageID, p.PlayerName, pl.Language
            FROM PlayerLanguageSpoken pl
            JOIN Players p ON pl.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pl.Language
        """)
        languages = cur.fetchall()
        
        for language in languages:
            print(f"ID: {language['PlayerLanguageID']}, "
                  f"Player: {language['PlayerName']}, "
                  f"Language: {language['Language']}")
        
        # Get language ID to delete
        while True:
            try:
                language_id = int(input("\nEnter Player Language ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # SQL query to delete player language
        query = "DELETE FROM PlayerLanguageSpoken WHERE PlayerLanguageID = %s"
        
        # Execute the query
        cur.execute(query, (language_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Player language with ID {language_id} deleted successfully!")
        else:
            print(f"No language record found with ID {language_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting player language record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a player language record
    """
    try:
        # Show current player languages
        print("Current Player Languages:")
        cur.execute("""
            SELECT pl.PlayerLanguageID, p.PlayerName, pl.Language
            FROM PlayerLanguageSpoken pl
            JOIN Players p ON pl.PlayerID = p.PlayerID
            ORDER BY p.PlayerName, pl.Language
        """)
        languages = cur.fetchall()
        
        for language in languages:
            print(f"ID: {language['PlayerLanguageID']}, "
                  f"Player: {language['PlayerName']}, "
                  f"Language: {language['Language']}")
        
        # Get language ID to update
        while True:
            try:
                language_id = int(input("\nEnter Player Language ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # Show available players
        print("\nAvailable Players:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, 
                   GROUP_CONCAT(pl.Language) as CurrentLanguages
            FROM Players p
            LEFT JOIN PlayerLanguageSpoken pl ON p.PlayerID = pl.PlayerID
            GROUP BY p.PlayerID, p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            languages = player['CurrentLanguages'] if player['CurrentLanguages'] else 'No languages registered'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Languages: {languages}")
        
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
        
        # Get new language (optional)
        language = input("Enter new Language (press enter to skip): ").strip()
        if language:
            language = language.capitalize()
        
        # If both player ID and language are provided, check for duplicates
        if player_id and language:
            cur.execute("""
                SELECT * FROM PlayerLanguageSpoken 
                WHERE PlayerID = %s AND Language = %s AND PlayerLanguageID != %s
            """, (player_id, language, language_id))
            
            if cur.fetchone():
                print("This language is already registered for this player.")
                return
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if player_id:
            update_fields.append("PlayerID = %s")
            params.append(player_id)
        if language:
            update_fields.append("Language = %s")
            params.append(language)
        
        if update_fields:
            # Add language ID to params
            params.append(language_id)
            
            query = f"UPDATE PlayerLanguageSpoken SET {', '.join(update_fields)} WHERE PlayerLanguageID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Player language record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating player language record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve player language records
    """
    try:
        # Option to retrieve all or specific player languages
        choice = input("Retrieve languages for (A)ll players or (S)pecific player? ").upper()
        
        if choice == 'A':
            # Retrieve all player languages
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pl.Language ORDER BY pl.Language) as Languages
            FROM Players p
            LEFT JOIN PlayerLanguageSpoken pl ON p.PlayerID = pl.PlayerID
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
            
            # Retrieve specific player's languages
            query = """
            SELECT p.PlayerID, p.PlayerName,
                   GROUP_CONCAT(pl.Language ORDER BY pl.Language) as Languages
            FROM Players p
            LEFT JOIN PlayerLanguageSpoken pl ON p.PlayerID = pl.PlayerID
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
                print(f"Languages: {result['Languages'] if result['Languages'] else 'None registered'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving player language records: {e}")
    except ValueError:
        print("Please enter a valid Player ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")