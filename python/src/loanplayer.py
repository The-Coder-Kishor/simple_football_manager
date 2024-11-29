# loanplayer.py
import pymysql
from datetime import datetime, date

def addRecord(con, cur):
    """
    Add a new loan player record
    """
    try:
        # Get player name from user
        player_name = input("Enter Player Name: ")
        
        # Check if player exists and is not already on loan
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, c.ClubName, p.ClubID
            FROM Players p
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerName LIKE %s
            AND p.PlayerID NOT IN (SELECT PlayerID FROM LoanPlayer)
        """, (f"%{player_name}%",))
        
        players = cur.fetchall()
        
        if not players:
            print("No eligible players found with that name or player is already on loan.")
            return
        
        # If multiple players found, let user select
        if len(players) > 1:
            print("\nMultiple players found:")
            for idx, player in enumerate(players, 1):
                club = player['ClubName'] if player['ClubName'] else 'No Club'
                print(f"{idx}. {player['PlayerName']} (Current Club: {club})")
            
            while True:
                try:
                    choice = int(input("\nSelect player number: ")) - 1
                    if 0 <= choice < len(players):
                        selected_player = players[choice]
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            selected_player = players[0]
        
        # Check if player is already in LoanPlayer table
        cur.execute("SELECT 1 FROM LoanPlayer WHERE PlayerID = %s", (selected_player['PlayerID'],))
        if cur.fetchone():
            print("This player is already registered as a loan player.")
            return
        
        # Get new club name for transfer
        new_club_name = input("Enter Club Name to transfer to: ")
        
        # Verify club exists
        cur.execute("SELECT ClubID FROM Clubs WHERE ClubName LIKE %s", (f"%{new_club_name}%",))
        new_club = cur.fetchone()
        if not new_club:
            print("Club not found.")
            return
        
        # Get dates
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
        
        # Insert into LoanPlayer
        cur.execute("""
            INSERT INTO LoanPlayer 
            (PlayerID, JoinDate, ContractEnd, OriginalClubID) 
            VALUES (%s, %s, %s, %s)
        """, (selected_player['PlayerID'], join_date, end_date, selected_player['ClubID']))
        
        # Update Players table with new club
        cur.execute("""
            UPDATE Players 
            SET ClubID = %s 
            WHERE PlayerID = %s
        """, (new_club['ClubID'], selected_player['PlayerID']))
        
        con.commit()
        print("Loan player record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding loan player record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a loan player record and restore original club
    """
    try:
        # Get player name from user
        player_name = input("Enter Player Name to remove from loan: ")
        
        # Find loan players matching the name
        cur.execute("""
            SELECT l.PlayerID, p.PlayerName, 
                   c.ClubName as CurrentClub,
                   oc.ClubName as OriginalClub,
                   l.JoinDate, l.ContractEnd,
                   l.OriginalClubID
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
            WHERE p.PlayerName LIKE %s
            ORDER BY p.PlayerName
        """, (f"%{player_name}%",))
        
        loan_players = cur.fetchall()
        
        if not loan_players:
            print("No loan players found with that name.")
            return
        
        # If multiple players found, let user select
        if len(loan_players) > 1:
            print("\nMultiple players found:")
            for idx, player in enumerate(loan_players, 1):
                current_club = player['CurrentClub'] if player['CurrentClub'] else 'No Current Club'
                print(f"\n{idx}. {player['PlayerName']}")
                print(f"   Original Club: {player['OriginalClub']}")
                print(f"   Current Club: {current_club}")
                print(f"   Loan Period: {player['JoinDate']} to {player['ContractEnd']}")
            
            while True:
                try:
                    choice = int(input("\nSelect player number: ")) - 1
                    if 0 <= choice < len(loan_players):
                        selected_player = loan_players[choice]
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            selected_player = loan_players[0]
            
        # Confirm deletion
        print(f"\nSelected Player: {selected_player['PlayerName']}")
        print(f"Original Club: {selected_player['OriginalClub']}")
        print(f"Current Club: {selected_player['CurrentClub']}")
        confirm = input("\nAre you sure you want to remove this loan record? (Y/N): ").upper()
        
        if confirm != 'Y':
            print("Operation cancelled.")
            return
            
        # Begin transaction
        cur.execute("START TRANSACTION")
        
        # Update Players table to restore original club
        cur.execute("""
            UPDATE Players 
            SET ClubID = %s 
            WHERE PlayerID = %s
        """, (selected_player['OriginalClubID'], selected_player['PlayerID']))
        
        # Delete from LoanPlayer table
        cur.execute("""
            DELETE FROM LoanPlayer 
            WHERE PlayerID = %s
        """, (selected_player['PlayerID'],))
        
        con.commit()
        print(f"\nLoan record deleted successfully!")
        print(f"Player {selected_player['PlayerName']} has been returned to {selected_player['OriginalClub']}")
    
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
        # Get player name from user
        player_name = input("Enter Player Name to update: ")
        
        # Find loan players matching the name
        cur.execute("""
            SELECT l.PlayerID, p.PlayerName, 
                   c.ClubName as CurrentClub,
                   oc.ClubName as OriginalClub,
                   l.JoinDate, l.ContractEnd,
                   l.OriginalClubID
            FROM LoanPlayer l
            JOIN Players p ON l.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
            WHERE p.PlayerName LIKE %s
            ORDER BY p.PlayerName
        """, (f"%{player_name}%",))
        
        loan_players = cur.fetchall()
        
        if not loan_players:
            print("No loan players found with that name.")
            return
        
        # If multiple players found, let user select
        if len(loan_players) > 1:
            print("\nMultiple players found:")
            for idx, player in enumerate(loan_players, 1):
                current_club = player['CurrentClub'] if player['CurrentClub'] else 'No Current Club'
                print(f"\n{idx}. {player['PlayerName']}")
                print(f"   Original Club: {player['OriginalClub']}")
                print(f"   Current Club: {current_club}")
                print(f"   Loan Period: {player['JoinDate']} to {player['ContractEnd']}")
            
            while True:
                try:
                    choice = int(input("\nSelect player number: ")) - 1
                    if 0 <= choice < len(loan_players):
                        selected_player = loan_players[choice]
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            selected_player = loan_players[0]

        print(f"\nUpdating loan record for {selected_player['PlayerName']}")
        print("Current Details:")
        print(f"Original Club: {selected_player['OriginalClub']}")
        print(f"Current Club: {selected_player['CurrentClub']}")
        print(f"Join Date: {selected_player['JoinDate']}")
        print(f"Contract End Date: {selected_player['ContractEnd']}")
        print("\nLeave field empty to keep current value")
        
        # New club update
        new_club_name = input("\nEnter new Club Name (or press Enter to keep current): ").strip()
        new_club_id = None
        if new_club_name:
            cur.execute("SELECT ClubID FROM Clubs WHERE ClubName LIKE %s", (f"%{new_club_name}%",))
            club = cur.fetchone()
            if club:
                new_club_id = club['ClubID']
            else:
                print("Club not found. Current club will be maintained.")
        
        # Join date update
        join_date = input("Enter new Join Date (YYYY-MM-DD) or press Enter to keep current: ").strip()
        if join_date:
            try:
                join_date_obj = datetime.strptime(join_date, '%Y-%m-%d').date()
                if join_date_obj > date.today():
                    print("Join date cannot be in the future. Current date will be maintained.")
                    join_date = None
            except ValueError:
                print("Invalid date format. Current date will be maintained.")
                join_date = None
        
        # Contract end date update
        end_date = input("Enter new Contract End Date (YYYY-MM-DD) or press Enter to keep current: ").strip()
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                join_date_to_check = (datetime.strptime(join_date, '%Y-%m-%d').date() 
                                    if join_date 
                                    else selected_player['JoinDate'])
                if end_date_obj <= join_date_to_check:
                    print("Contract end date must be after join date. Current date will be maintained.")
                    end_date = None
            except ValueError:
                print("Invalid date format. Current date will be maintained.")
                end_date = None

        # Prepare update queries
        updates_needed = False
        
        # Start transaction
        cur.execute("START TRANSACTION")
        
        # Update club if changed
        if new_club_id:
            cur.execute("""
                UPDATE Players 
                SET ClubID = %s 
                WHERE PlayerID = %s
            """, (new_club_id, selected_player['PlayerID']))
            updates_needed = True
        
        # Update loan dates if changed
        loan_updates = []
        loan_params = []
        
        if join_date:
            loan_updates.append("JoinDate = %s")
            loan_params.append(join_date)
            updates_needed = True
            
        if end_date:
            loan_updates.append("ContractEnd = %s")
            loan_params.append(end_date)
            updates_needed = True
            
        if loan_updates:
            loan_params.append(selected_player['PlayerID'])
            query = f"UPDATE LoanPlayer SET {', '.join(loan_updates)} WHERE PlayerID = %s"
            cur.execute(query, loan_params)
        
        if updates_needed:
            con.commit()
            print("\nLoan player record updated successfully!")
            
            # Show updated details
            cur.execute("""
                SELECT p.PlayerName, c.ClubName as CurrentClub, 
                       l.JoinDate, l.ContractEnd
                FROM LoanPlayer l
                JOIN Players p ON l.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                WHERE l.PlayerID = %s
            """, (selected_player['PlayerID'],))
            
            updated = cur.fetchone()
            print("\nUpdated Details:")
            print(f"Player: {updated['PlayerName']}")
            print(f"Current Club: {updated['CurrentClub']}")
            print(f"Join Date: {updated['JoinDate']}")
            print(f"Contract End: {updated['ContractEnd']}")
        else:
            print("\nNo updates were specified.")
            con.rollback()
    
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
        # Option to retrieve all or specific club
        choice = input("Retrieve (A)ll loan players or (S)pecific club? ").upper()
        
        if choice == 'A':
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
            # Get club name from user
            club_name = input("Enter Club Name: ")
            
            # Find club
            cur.execute("""
                SELECT ClubID, ClubName 
                FROM Clubs 
                WHERE ClubName LIKE %s
                ORDER BY ClubName
            """, (f"%{club_name}%",))
            
            clubs = cur.fetchall()
            
            if not clubs:
                print("No clubs found with that name.")
                return
                
            # If multiple clubs found, let user select
            if len(clubs) > 1:
                print("\nMultiple clubs found:")
                for idx, club in enumerate(clubs, 1):
                    print(f"{idx}. {club['ClubName']}")
                
                while True:
                    try:
                        choice = int(input("\nSelect club number: ")) - 1
                        if 0 <= choice < len(clubs):
                            selected_club = clubs[choice]
                            break
                        print("Invalid selection.")
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                selected_club = clubs[0]
            
            # Ask user whether to search by original or current club
            while True:
                club_type = input("\nSearch for players where this is the (O)riginal club, (C)urrent club, or (B)oth? ").upper()
                if club_type in ['O', 'C', 'B']:
                    break
                print("Please enter O, C, or B.")

            print(f"\nRetrieving loan players for {selected_club['ClubName']}")
            
            # Modify query based on user choice
            if club_type == 'O':
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
                print(f"\nShowing players loaned OUT from {selected_club['ClubName']}")
                cur.execute(query, (selected_club['ClubID'],))
            
            elif club_type == 'C':
                query = """
                SELECT l.*, p.PlayerName, p.MarketValue,
                       c.ClubName as CurrentClub,
                       oc.ClubName as OriginalClub,
                       DATEDIFF(l.ContractEnd, CURDATE()) as DaysRemaining
                FROM LoanPlayer l
                JOIN Players p ON l.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
                WHERE p.ClubID = %s
                ORDER BY l.ContractEnd
                """
                print(f"\nShowing players loaned IN to {selected_club['ClubName']}")
                cur.execute(query, (selected_club['ClubID'],))
            
            else:  # 'B'
                query = """
                SELECT l.*, p.PlayerName, p.MarketValue,
                       c.ClubName as CurrentClub,
                       oc.ClubName as OriginalClub,
                       DATEDIFF(l.ContractEnd, CURDATE()) as DaysRemaining
                FROM LoanPlayer l
                JOIN Players p ON l.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                JOIN Clubs oc ON l.OriginalClubID = oc.ClubID
                WHERE l.OriginalClubID = %s OR p.ClubID = %s
                ORDER BY l.ContractEnd
                """
                print(f"\nShowing ALL loan players related to {selected_club['ClubName']}")
                cur.execute(query, (selected_club['ClubID'], selected_club['ClubID']))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No loan players found.")
        else:
            print("\nLoan Player Details:")
            for player in results:
                print("\n-----------------------------------")
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
            print("-----------------------------------")
            print(f"\nTotal players found: {len(results)}")
    
    except pymysql.Error as e:
        print(f"Error retrieving loan player records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")