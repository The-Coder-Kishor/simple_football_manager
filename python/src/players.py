import pymysql
from datetime import datetime

def search_players_by_name(cur, name):
    """
    Search for players by name and return matching records
    
    Args:
        cur (pymysql.cursors.Cursor): Database cursor
        name (str): Partial or full player name to search
    
    Returns:
        list: List of matching player records
    """
    query = """
    SELECT p.PlayerID, p.PlayerName, c.ClubName 
    FROM Players p 
    LEFT JOIN Clubs c ON p.ClubID = c.ClubID 
    WHERE p.PlayerName LIKE %s
    """
    cur.execute(query, (f'%{name}%',))
    return cur.fetchall()

def addRecord(con, cur):
    """
    Add a new player record
    """
    try:
        # Collect player details
        player_name = input("Enter Player Name: ")
        
        # Birth date validation
        while True:
            birth_date = input("Enter Birth Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Market value validation
        while True:
            try:
                market_value = float(input("Enter Market Value: "))
                break
            except ValueError:
                print("Please enter a valid number for market value.")
        
        # Height validation
        while True:
            try:
                height = float(input("Enter Height (in cm): "))
                break
            except ValueError:
                print("Please enter a valid number for height.")
        
        # Weight validation
        while True:
            try:
                weight = float(input("Enter Weight (in kg): "))
                break
            except ValueError:
                print("Please enter a valid number for weight.")
        
        # Jersey number validation
        while True:
            try:
                jersey_number = int(input("Enter Jersey Number (1-99): "))
                if 1 <= jersey_number <= 99:
                    break
                print("Jersey number must be between 1 and 99.")
            except ValueError:
                print("Please enter a valid integer for jersey number.")
        
        # Overall rating validation
        while True:
            try:
                overall_rating = float(input("Enter Overall Rating (0-10): "))
                if 0 <= overall_rating <= 10:
                    break
                print("Overall rating must be between 0 and 10.")
            except ValueError:
                print("Please enter a valid number for overall rating.")
        
        work_rate = input("Enter Work Rate (High/Medium/Low): ").capitalize()
        
        # Aggressiveness validation
        while True:
            try:
                aggressiveness = int(input("Enter Aggressiveness (1-10): "))
                if 1 <= aggressiveness <= 10:
                    break
                print("Aggressiveness must be between 1 and 10.")
            except ValueError:
                print("Please enter a valid integer for aggressiveness.")
        
        # Show available clubs
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
        
        # Get club ID (optional)
        club_id = input("Enter Club ID (press enter to skip): ")
        club_id = int(club_id) if club_id else None
        
        # Show available players for mentor selection
        print("\nAvailable Players (potential mentors):")
        cur.execute("SELECT PlayerID, PlayerName FROM Players")
        players = cur.fetchall()
        for player in players:
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")
        
        # Get mentor ID (optional)
        mentor_id = input("Enter Mentor Player ID (press enter to skip): ")
        mentor_id = int(mentor_id) if mentor_id else None
        
        # SQL query to insert player
        query = """
        INSERT INTO Players 
        (PlayerName, BirthDate, MarketValue, Height, Weight, JerseyNumber, 
         OverallRating, WorkRate, Aggressiveness, ClubID, MentorID) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_name, birth_date, market_value, height, weight, 
                          jersey_number, overall_rating, work_rate, aggressiveness, 
                          club_id, mentor_id))
        con.commit()
        
        print("Player record added successfully!")
        print(f"New Player: {player_name}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")
        
def deleteRecord(con, cur):
    """
    Delete a player record by name
    """
    try:
        # Get player name to search
        player_name = input("Enter Player Name (or part of name) to delete: ")
        
        # Search for players
        players = search_players_by_name(cur, player_name)
        
        if not players:
            print(f"No players found matching '{player_name}'.")
            return
        
        # Display matching players
        print("Matching Players:")
        for player in players:
            club_name = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}, Club: {club_name}")
        
        # Get player ID to delete
        while True:
            try:
                player_id = int(input("Enter Player ID to delete: "))
                # Verify the ID is from the search results
                if any(player['PlayerID'] == player_id for player in players):
                    break
                else:
                    print("Please choose a Player ID from the displayed list.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # SQL query to delete player
        query = "DELETE FROM Players WHERE PlayerID = %s"
        
        # Execute the query
        cur.execute(query, (player_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Player with ID {player_id} deleted successfully!")
        else:
            print(f"No player found with ID {player_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a player record by name
    """
    try:
        # Get player name to search
        player_name = input("Enter Player Name (or part of name) to update: ")
        
        # Search for players
        players = search_players_by_name(cur, player_name)
        
        if not players:
            print(f"No players found matching '{player_name}'.")
            return
        
        # Display matching players
        print("Matching Players:")
        for player in players:
            club_name = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}, Club: {club_name}")
        
        # Get player ID to update
        while True:
            try:
                player_id = int(input("Enter Player ID to update: "))
                # Verify the ID is from the search results
                if any(player['PlayerID'] == player_id for player in players):
                    break
                else:
                    print("Please choose a Player ID from the displayed list.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Rest of the update function remains the same as in the original code
        # (All the existing update logic from the previous implementation)
        # [The existing update code block is copied here from the previous implementation]
        # Collect new details (allow skipping)
        player_name = input("Enter new Player Name (press enter to skip): ")
        
        birth_date = input("Enter new Birth Date (YYYY-MM-DD) (press enter to skip): ")
        if birth_date:
            while True:
                try:
                    datetime.strptime(birth_date, '%Y-%m-%d')
                    break
                except ValueError:
                    birth_date = input("Please enter a valid date in YYYY-MM-DD format: ")
        
        # ... [rest of the existing update function code remains the same]
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve player records
    """
    try:
        # Option to retrieve all or specific player
        choice = input("Retrieve (A)ll or (S)pecific player or by (C)lub? ").upper()
        
        if choice == 'A':
            # Retrieve all players with related information
            query = """
            SELECT p.*, 
                   c.ClubName,
                   m.PlayerName as MentorName
            FROM Players p 
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID 
            LEFT JOIN Players m ON p.MentorID = m.PlayerID
            """
            cur.execute(query)
        elif choice == 'S':
            # Search by player name
            player_name = input("Enter Player Name (or part of name): ")
            query = """
            SELECT p.*, 
                   c.ClubName,
                   m.PlayerName as MentorName
            FROM Players p 
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID 
            LEFT JOIN Players m ON p.MentorID = m.PlayerID
            WHERE p.PlayerName LIKE %s
            """
            cur.execute(query, (f'%{player_name}%',))
        
        elif choice == 'C':
            # Take club name as input
            club_name = input("Enter Club Name to retrieve players: ")
        
            # Retrieve all players with related information for the specified club
            query = """
            SELECT p.*, 
                   c.ClubName,
                   m.PlayerName as MentorName
            FROM Players p 
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID 
            LEFT JOIN Players m ON p.MentorID = m.PlayerID
            WHERE c.ClubName LIKE %s
            """
            cur.execute(query, ('%' + club_name + '%',))
            
        else: 
            print('invalid option')
            return
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No players found.")
        else:
            for player in results:
                print("\nPlayer Details:")
                print(f"Player ID: {player['PlayerID']}")
                print(f"Name: {player['PlayerName']}")
                print(f"Birth Date: {player['BirthDate']}")
                print(f"Market Value: ${player['MarketValue']:,.2f}")
                print(f"Height: {player['Height']} cm")
                print(f"Weight: {player['Weight']} kg")
                print(f"Jersey Number: {player['JerseyNumber']}")
                print(f"Overall Rating: {player['OverallRating']}")
                print(f"Work Rate: {player['WorkRate']}")
                print(f"Aggressiveness: {player['Aggressiveness']}")
                print(f"Club: {player['ClubName'] if player['ClubName'] else 'No Club'}")
                print(f"Mentor: {player['MentorName'] if player['MentorName'] else 'No Mentor'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving player records: {e}")
    except ValueError:
        print("Please enter a valid Player ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")