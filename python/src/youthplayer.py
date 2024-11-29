# youthplayer.py
import pymysql
from datetime import datetime, date

def addRecord(con, cur):
    """
    Add a new youth player record
    """
    try:
        # Show available players who are not already youth players
        print("Available Players (Not currently youth players):")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, p.BirthDate, c.ClubName
            FROM Players p
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerID NOT IN (SELECT PlayerID FROM YouthPlayer)
            ORDER BY p.PlayerName
        """)
        players = cur.fetchall()
        
        if not players:
            print("No eligible players found for youth registration.")
            return
        
        for player in players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}, "
                  f"Birth Date: {player['BirthDate']}, Club: {club}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists and is not already a youth player
                cur.execute("""
                    SELECT p.PlayerID, p.BirthDate 
                    FROM Players p 
                    WHERE p.PlayerID = %s 
                    AND p.PlayerID NOT IN (SELECT PlayerID FROM YouthPlayer)
                """, (player_id,))
                player = cur.fetchone()
                if player:
                    # Check if player is under 21
                    birth_date = player['BirthDate']
                    age = (date.today() - birth_date).days / 365.25
                    if age > 21:
                        print("Player is too old for youth registration (must be under 21).")
                        return
                    break
                print("Invalid Player ID or player is already registered as youth player.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Academy join date validation
        while True:
            join_date = input("Enter Academy Join Date (YYYY-MM-DD): ")
            try:
                join_date_obj = datetime.strptime(join_date, '%Y-%m-%d').date()
                if join_date_obj > date.today():
                    print("Join date cannot be in the future.")
                    continue
                if (join_date_obj - birth_date).days < 0:
                    print("Join date cannot be before birth date.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Expected graduation date validation
        while True:
            grad_date = input("Enter Expected Graduation Date (YYYY-MM-DD): ")
            try:
                grad_date_obj = datetime.strptime(grad_date, '%Y-%m-%d').date()
                if grad_date_obj <= join_date_obj:
                    print("Graduation date must be after join date.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Youth level validation (typically 1-5)
        while True:
            try:
                youth_level = int(input("Enter Youth Level (1-5): "))
                if 1 <= youth_level <= 5:
                    break
                print("Youth level must be between 1 and 5.")
            except ValueError:
                print("Please enter a valid integer for youth level.")
        
        # SQL query to insert youth player
        query = """
        INSERT INTO YouthPlayer 
        (PlayerID, AcademyJoinDate, ExpectedGraduation, YouthLevel) 
        VALUES (%s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, join_date, grad_date, youth_level))
        con.commit()
        
        print("Youth player record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding youth player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a youth player record
    """
    try:
        # Show current youth players
        print("Current Youth Players:")
        cur.execute("""
            SELECT y.PlayerID, p.PlayerName, p.BirthDate, 
                   y.AcademyJoinDate, y.ExpectedGraduation, y.YouthLevel,
                   c.ClubName
            FROM YouthPlayer y
            JOIN Players p ON y.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            ORDER BY p.PlayerName
        """)
        youth_players = cur.fetchall()
        
        for player in youth_players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Birth Date: {player['BirthDate']}")
            print(f"Academy Join Date: {player['AcademyJoinDate']}")
            print(f"Expected Graduation: {player['ExpectedGraduation']}")
            print(f"Youth Level: {player['YouthLevel']}")
            print(f"Club: {club}")
        
        # Get player ID to delete
        while True:
            try:
                player_id = int(input("\nEnter Player ID to delete from youth system: "))
                break
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # SQL query to delete youth player
        query = "DELETE FROM YouthPlayer WHERE PlayerID = %s"
        
        # Execute the query
        cur.execute(query, (player_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Youth player with ID {player_id} deleted successfully!")
        else:
            print(f"No youth player found with ID {player_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting youth player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a youth player record
    """
    try:
        # Show current youth players
        print("Current Youth Players:")
        cur.execute("""
            SELECT y.PlayerID, p.PlayerName, p.BirthDate, 
                   y.AcademyJoinDate, y.ExpectedGraduation, y.YouthLevel,
                   c.ClubName
            FROM YouthPlayer y
            JOIN Players p ON y.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            ORDER BY p.PlayerName
        """)
        youth_players = cur.fetchall()
        
        for player in youth_players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Birth Date: {player['BirthDate']}")
            print(f"Academy Join Date: {player['AcademyJoinDate']}")
            print(f"Expected Graduation: {player['ExpectedGraduation']}")
            print(f"Youth Level: {player['YouthLevel']}")
            print(f"Club: {club}")
        
        # Get player ID to update
        while True:
            try:
                player_id = int(input("\nEnter Player ID to update: "))
                # Verify youth player exists
                cur.execute("SELECT * FROM YouthPlayer WHERE PlayerID = %s", (player_id,))
                if cur.fetchone():
                    break
                print("No youth player found with this ID.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Get current record details
        cur.execute("""
            SELECT y.*, p.BirthDate 
            FROM YouthPlayer y
            JOIN Players p ON y.PlayerID = p.PlayerID
            WHERE y.PlayerID = %s
        """, (player_id,))
        current = cur.fetchone()
        
        # Collect new details (allow skipping)
        print("\nPress Enter to keep current values:")
        
        # Academy join date update
        join_date = input(f"Enter new Academy Join Date (current: {current['AcademyJoinDate']}, YYYY-MM-DD): ")
        if join_date:
            try:
                join_date_obj = datetime.strptime(join_date, '%Y-%m-%d').date()
                if join_date_obj > date.today():
                    print("Join date cannot be in the future. Value not updated.")
                    join_date = None
                elif (join_date_obj - current['BirthDate']).days < 0:
                    print("Join date cannot be before birth date. Value not updated.")
                    join_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                join_date = None
        
        # Expected graduation date update
        grad_date = input(f"Enter new Expected Graduation Date (current: {current['ExpectedGraduation']}, YYYY-MM-DD): ")
        if grad_date:
            try:
                grad_date_obj = datetime.strptime(grad_date, '%Y-%m-%d').date()
                join_date_to_check = join_date_obj if join_date else current['AcademyJoinDate']
                if grad_date_obj <= join_date_to_check:
                    print("Graduation date must be after join date. Value not updated.")
                    grad_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                grad_date = None
        
        # Youth level update
        youth_level = input(f"Enter new Youth Level (current: {current['YouthLevel']}, 1-5): ")
        if youth_level:
            try:
                youth_level = int(youth_level)
                if not (1 <= youth_level <= 5):
                    print("Youth level must be between 1 and 5. Value not updated.")
                    youth_level = None
            except ValueError:
                print("Invalid youth level. Value not updated.")
                youth_level = None
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if join_date:
            update_fields.append("AcademyJoinDate = %s")
            params.append(join_date)
        if grad_date:
            update_fields.append("ExpectedGraduation = %s")
            params.append(grad_date)
        if youth_level:
            update_fields.append("YouthLevel = %s")
            params.append(youth_level)
        
        if update_fields:
            # Add player ID to params
            params.append(player_id)
            
            query = f"UPDATE YouthPlayer SET {', '.join(update_fields)} WHERE PlayerID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Youth player record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating youth player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve youth player records
    """
    try:
        # Option to retrieve all or specific youth player
        choice = input("Retrieve (A)ll youth players or (S)pecific player or Specific (C)lub wise? ").upper()
        
        if choice == 'A':
            # Option to filter by youth level
            filter_choice = input("Filter by youth level? (Y/N): ").upper()
            
            if filter_choice == 'Y':
                level = int(input("Enter youth level (1-5): "))
                query = """
                SELECT y.*, p.PlayerName, p.BirthDate, c.ClubName,
                       TIMESTAMPDIFF(YEAR, p.BirthDate, CURDATE()) as Age,
                       DATEDIFF(y.ExpectedGraduation, CURDATE()) as DaysToGraduation
                FROM YouthPlayer y
                JOIN Players p ON y.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                WHERE y.YouthLevel = %s
                ORDER BY p.PlayerName
                """
                cur.execute(query, (level,))
            else:
                query = """
                SELECT y.*, p.PlayerName, p.BirthDate, c.ClubName,
                       TIMESTAMPDIFF(YEAR, p.BirthDate, CURDATE()) as Age,
                       DATEDIFF(y.ExpectedGraduation, CURDATE()) as DaysToGraduation
                FROM YouthPlayer y
                JOIN Players p ON y.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                ORDER BY p.PlayerName
                """
                cur.execute(query)
        elif choice == 'S':
            # Get specific player ID
            player_id = int(input("Enter Player ID: "))
            query = """
            SELECT y.*, p.PlayerName, p.BirthDate, c.ClubName,
                   TIMESTAMPDIFF(YEAR, p.BirthDate, CURDATE()) as Age,
                   DATEDIFF(y.ExpectedGraduation, CURDATE()) as DaysToGraduation
            FROM YouthPlayer y
            JOIN Players p ON y.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE y.PlayerID = %s
            """
            cur.execute(query, (player_id,))
        elif choice == 'C':
            club_name = input("Enter Club Name to retrieve youth players: ")
            query = """
            SELECT y.*, p.PlayerName, p.BirthDate, c.ClubName,
                   TIMESTAMPDIFF(YEAR, p.BirthDate, CURDATE()) as Age,
                   DATEDIFF(y.ExpectedGraduation, CURDATE()) as DaysToGraduation
            FROM YouthPlayer y
            JOIN Players p ON y.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE c.ClubName LIKE %s
            ORDER BY p.PlayerName
            """
            cur.execute(query, ('%' + club_name + '%',))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No youth players found.")
        else:
            for player in results:
                print("\nYouth Player Details:")
                print(f"Player ID: {player['PlayerID']}")
                print(f"Name: {player['PlayerName']}")
                print(f"Age: {player['Age']} years")
                print(f"Club: {player['ClubName'] if player['ClubName'] else 'No Club'}")
                print(f"Youth Level: {player['YouthLevel']}")
                print(f"Academy Join Date: {player['AcademyJoinDate']}")
                print(f"Expected Graduation: {player['ExpectedGraduation']}")
                days_to_grad = player['DaysToGraduation']
                if days_to_grad > 0:
                    print(f"Days until graduation: {days_to_grad}")
                else:
                    print("Graduation date has passed")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving youth player records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")