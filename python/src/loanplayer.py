# loanplayer.py
import pymysql
from datetime import datetime, date

def addRecord(con, cur):
    """
    Add a new loan player record
    """
    try:
        # Show available players who are not already loan players
        print("Available Players (Not currently on loan):")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, c.ClubName, p.MarketValue
            FROM Players p
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerID NOT IN (SELECT PlayerID FROM LoanPlayer)
            ORDER BY p.PlayerName
        """)
        players = cur.fetchall()
        
        if not players:
            print("No eligible players found for loan registration.")
            return
        
        for player in players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Current Club: {club}")
            print(f"Market Value: ${player['MarketValue']:,.2f}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists and is not already on loan
                cur.execute("""
                    SELECT p.PlayerID, p.ClubID 
                    FROM Players p 
                    WHERE p.PlayerID = %s 
                    AND p.PlayerID NOT IN (SELECT PlayerID FROM LoanPlayer)
                """, (player_id,))
                player = cur.fetchone()
                if player:
                    if not player['ClubID']:
                        print("Player must have a current club to be loaned.")
                        return
                    break
                print("Invalid Player ID or player is already registered as loan player.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Join date validation
        while True:
            join_date = input("Enter Loan Join Date (YYYY-MM-DD): ")
            try:
                join_date_obj = datetime.strptime(join_date, '%Y-%m-%d').date()
                if join_date_obj > date.today():
                    print("Join date cannot be in the future.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Contract end date validation
        while True:
            end_date = input("Enter Loan Contract End Date (YYYY-MM-DD): ")
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                if end_date_obj <= join_date_obj:
                    print("Contract end date must be after join date.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Get original club (current club of the player)
        cur.execute("""
            SELECT c.ClubID, c.ClubName 
            FROM Players p
            JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerID = %s
        """, (player_id,))
        original_club = cur.fetchone()
        
        # SQL query to insert loan player
        query = """
        INSERT INTO LoanPlayer 
        (PlayerID, JoinDate, ContractEnd, OriginalClubID) 
        VALUES (%s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, join_date, end_date, original_club['ClubID']))
        con.commit()
        
        print("Loan player record added successfully!")
        print(f"Original Club: {original_club['ClubName']}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding loan player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a loan player record
    """
    try:
        # Show current loan players
        print("Current Loan Players:")
        cur.execute("""
            SELECT l.PlayerID, p.PlayerName, 
                   c.ClubName as CurrentClub,
                   oc.ClubName as OriginalClub,
                   l.JoinDate, l.ContractEnd
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
            ORDER BY p.PlayerName
        """)
        loan_players = cur.fetchall()
        
        for player in loan_players:
            current_club = player['CurrentClub'] if player['CurrentClub'] else 'No Current Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Original Club: {player['OriginalClub']}")
            print(f"Current Club: {current_club}")
            print(f"Loan Period: {player['JoinDate']} to {player['ContractEnd']}")
        
        # Get player ID to delete
        while True:
            try:
                player_id = int(input("\nEnter Player ID to remove from loan: "))
                break
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # SQL query to delete loan player
        query = "DELETE FROM LoanPlayer WHERE PlayerID = %s"
        
        # Execute the query
        cur.execute(query, (player_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Loan player with ID {player_id} removed successfully!")
        else:
            print(f"No loan player found with ID {player_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting loan player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a loan player record
    """
    try:
        # Show current loan players
        print("Current Loan Players:")
        cur.execute("""
            SELECT l.PlayerID, p.PlayerName, 
                   c.ClubName as CurrentClub,
                   oc.ClubName as OriginalClub,
                   l.JoinDate, l.ContractEnd
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
            ORDER BY p.PlayerName
        """)
        loan_players = cur.fetchall()
        
        for player in loan_players:
            current_club = player['CurrentClub'] if player['CurrentClub'] else 'No Current Club'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Original Club: {player['OriginalClub']}")
            print(f"Current Club: {current_club}")
            print(f"Loan Period: {player['JoinDate']} to {player['ContractEnd']}")
        
        # Get player ID to update
        while True:
            try:
                player_id = int(input("\nEnter Player ID to update: "))
                # Verify loan player exists
                cur.execute("SELECT * FROM LoanPlayer WHERE PlayerID = %s", (player_id,))
                if cur.fetchone():
                    break
                print("No loan player found with this ID.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Get current record details
        cur.execute("""
            SELECT l.*, p.PlayerName 
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            WHERE l.PlayerID = %s
        """, (player_id,))
        current = cur.fetchone()
        
        print(f"\nUpdating loan record for {current['PlayerName']}")
        print("Press Enter to keep current values:")
        
        # Join date update
        join_date = input(f"Enter new Join Date (current: {current['JoinDate']}, YYYY-MM-DD): ")
        if join_date:
            try:
                join_date_obj = datetime.strptime(join_date, '%Y-%m-%d').date()
                if join_date_obj > date.today():
                    print("Join date cannot be in the future. Value not updated.")
                    join_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                join_date = None
        
        # Contract end date update
        end_date = input(f"Enter new Contract End Date (current: {current['ContractEnd']}, YYYY-MM-DD): ")
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                join_date_to_check = join_date_obj if join_date else current['JoinDate']
                if end_date_obj <= join_date_to_check:
                    print("Contract end date must be after join date. Value not updated.")
                    end_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                end_date = None
        
        # Original club cannot be updated as it's a historical record
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if join_date:
            update_fields.append("JoinDate = %s")
            params.append(join_date)
        if end_date:
            update_fields.append("ContractEnd = %s")
            params.append(end_date)
        
        if update_fields:
            # Add player ID to params
            params.append(player_id)
            
            query = f"UPDATE LoanPlayer SET {', '.join(update_fields)} WHERE PlayerID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Loan player record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating loan player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve loan player records
    """
    try:
        # Option to retrieve all or specific loan player
        choice = input("Retrieve (A)ll loan players or (S)pecific player? ").upper()
        
        if choice == 'A':
            # Option to filter by original club
            filter_choice = input("Filter by original club? (Y/N): ").upper()
            
            if filter_choice == 'Y':
                # Show available clubs
                print("\nAvailable Clubs:")
                cur.execute("SELECT ClubID, ClubName FROM Clubs ORDER BY ClubName")
                clubs = cur.fetchall()
                for club in clubs:
                    print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
                
                club_id = int(input("\nEnter Club ID: "))
                query = """
                SELECT l.*, p.PlayerName, p.MarketValue,
                       c.ClubName as CurrentClub,
                       oc.ClubName as OriginalClub,
                       DATEDIFF(l.ContractEnd, CURDATE()) as DaysRemaining
                FROM LoanPlayer l
                JOIN Players p ON l.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
                WHERE l.OriginalClubID = %s
                ORDER BY l.ContractEnd
                """
                cur.execute(query, (club_id,))
            else:
                query = """
                SELECT l.*, p.PlayerName, p.MarketValue,
                       c.ClubName as CurrentClub,
                       oc.ClubName as OriginalClub,
                       DATEDIFF(l.ContractEnd, CURDATE()) as DaysRemaining
                FROM LoanPlayer l
                JOIN Players p ON l.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
                ORDER BY l.ContractEnd
                """
                cur.execute(query)
        else:
            # Get specific player ID
            player_id = int(input("Enter Player ID: "))
            query = """
            SELECT l.*, p.PlayerName, p.MarketValue,
                   c.ClubName as CurrentClub,
                   oc.ClubName as OriginalClub,
                   DATEDIFF(l.ContractEnd, CURDATE()) as DaysRemaining
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
            WHERE l.PlayerID = %s
            """
            cur.execute(query, (player_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No loan players found.")
        else:
            for player in results:
                print("\nLoan Player Details:")
                print(f"Player ID: {player['PlayerID']}")
                print(f"Name: {player['PlayerName']}")
                print(f"Market Value: ${player['MarketValue']:,.2f}")
                print(f"Original Club: {player['OriginalClub']}")
                print(f"Current Club: {player['CurrentClub'] if player['CurrentClub'] else 'No Current Club'}")
                print(f"Loan Period: {player['JoinDate']} to {player['ContractEnd']}")
                days_remaining = player['DaysRemaining']
                if days_remaining > 0:
                    print(f"Days Remaining: {days_remaining}")
                else:
                    print("Loan period has ended")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving loan player records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")