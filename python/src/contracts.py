import pymysql
from datetime import datetime

def find_unique_player_by_name(cur, player_name):
    """
    Find a unique player by name. Returns player_id if exactly one match, otherwise None.
    """
    cur.execute("SELECT PlayerID FROM Players WHERE PlayerName = %s", (player_name,))
    results = cur.fetchall()
    
    if len(results) == 1:
        return results[0]['PlayerID']
    elif len(results) == 0:
        print(f"No player found with name: {player_name}")
    else:
        print(f"Multiple players found with name: {player_name}")
    return None

def find_unique_club_by_name(cur, club_name):
    """
    Find a unique club by name. Returns club_id if exactly one match, otherwise None.
    """
    cur.execute("SELECT ClubID FROM Clubs WHERE ClubName = %s", (club_name,))
    results = cur.fetchall()
    
    if len(results) == 1:
        return results[0]['ClubID']
    elif len(results) == 0:
        print(f"No club found with name: {club_name}")
    else:
        print(f"Multiple clubs found with name: {club_name}")
    return None

def addRecord(con, cur):
    """
    Add a new contract record with specific requirements
    """
    try:
        # Get player name and validate
        player_name = input("Enter Player Name: ")
        player_id = find_unique_player_by_name(cur, player_name)
        if not player_id:
            return
        
        # Get club name and validate
        club_name = input("Enter Club Name: ")
        club_id = find_unique_club_by_name(cur, club_name)
        if not club_id:
            return
        
        # Find player's latest contract and set its validity to 0
        cur.execute("""
            SELECT ContractID 
            FROM Contracts 
            WHERE PlayerID = %s 
            ORDER BY EndDate DESC 
            LIMIT 1
        """, (player_id,))
        
        latest_contract = cur.fetchone()
        if latest_contract:
            cur.execute("""
                UPDATE Contracts 
                SET Validity = 0 
                WHERE ContractID = %s
            """, (latest_contract['ContractID'],))
        
        # Input new contract details (unchanged from original)
        # Start date validation
        while True:
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # End date validation
        while True:
            end_date = input("Enter End Date (YYYY-MM-DD): ")
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                if end_date_obj > start_date_obj:
                    break
                print("End date must be after start date.")
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Salary validation
        while True:
            try:
                salary = float(input("Enter Salary: "))
                if salary > 0:
                    break
                print("Salary must be greater than 0.")
            except ValueError:
                print("Please enter a valid number for salary.")
        
        # SQL query to insert contract
        query = """
        INSERT INTO Contracts 
        (StartDate, EndDate, Salary, Validity, ClubID, PlayerID) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (start_date, end_date, salary, True, club_id, player_id))
        con.commit()
        
        print("Contract record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding contract record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a contract record by setting validity to 0
    """
    try:
        # Get player name and validate
        player_name = input("Enter Player Name: ")
        player_id = find_unique_player_by_name(cur, player_name)
        if not player_id:
            return
        
        # Get club name and validate
        club_name = input("Enter Club Name: ")
        club_id = find_unique_club_by_name(cur, club_name)
        if not club_id:
            return
        
        # Find the specific contract to invalidate
        cur.execute("""
            SELECT ContractID 
            FROM Contracts 
            WHERE PlayerID = %s AND ClubID = %s AND Validity = 1
        """, (player_id, club_id))
        
        contract = cur.fetchone()
        if contract:
            cur.execute("""
                UPDATE Contracts 
                SET Validity = 0 
                WHERE ContractID = %s
            """, (contract['ContractID'],))
            con.commit()
            print(f"Contract for {player_name} at {club_name} set to inactive.")
        else:
            print(f"No active contract found for {player_name} at {club_name}.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting contract record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a contract record by searching with player and club names
    """
    try:
        # Get player name and validate
        player_name = input("Enter Player Name: ")
        player_id = find_unique_player_by_name(cur, player_name)
        if not player_id:
            return
        
        # Get club name and validate
        club_name = input("Enter Club Name: ")
        club_id = find_unique_club_by_name(cur, club_name)
        if not club_id:
            return
        
        # Find the specific active contract
        cur.execute("""
            SELECT * FROM Contracts 
            WHERE PlayerID = %s AND ClubID = %s AND Validity = 1
        """, (player_id, club_id))
        
        current_contract = cur.fetchone()
        if not current_contract:
            print(f"No active contract found for {player_name} at {club_name}.")
            return
        
        # Contract ID for later use
        contract_id = current_contract['ContractID']
        
        # Collect new details (allow skipping)
        print("\nEnter new details (press enter to keep current value)")
        
        # Start date input
        start_date = input(f"Current Start Date: {current_contract['StartDate']}. Enter new Start Date (YYYY-MM-DD): ").strip()
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Start date not updated.")
                start_date = None
        
        # End date input
        end_date = input(f"Current End Date: {current_contract['EndDate']}. Enter new End Date (YYYY-MM-DD): ").strip()
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                
                # Validate date order
                if start_date:
                    if end_date_obj <= start_date_obj:
                        print("End date must be after start date. Dates not updated.")
                        start_date = end_date = None
                else:
                    if end_date_obj <= current_contract['StartDate']:
                        print("End date must be after start date. End date not updated.")
                        end_date = None
            except ValueError:
                print("Invalid date format. End date not updated.")
                end_date = None
        
        # Salary input
        salary = input(f"Current Salary: ${current_contract['Salary']:,.2f}. Enter new Salary: ").strip()
        if salary:
            try:
                salary = float(salary)
                if salary <= 0:
                    print("Salary must be greater than 0. Salary not updated.")
                    salary = None
            except ValueError:
                print("Invalid salary format. Salary not updated.")
                salary = None
        
        # Check for overlapping contracts
        # Prepare parameters for overlap check
        check_start_date = start_date if start_date else str(current_contract['StartDate'])
        check_end_date = end_date if end_date else str(current_contract['EndDate'])
        
        cur.execute("""
            SELECT * FROM Contracts 
            WHERE PlayerID = %s AND Validity = 1 AND ContractID != %s
            AND ((StartDate BETWEEN %s AND %s) 
            OR (EndDate BETWEEN %s AND %s)
            OR (StartDate <= %s AND EndDate >= %s))
        """, (player_id, contract_id, check_start_date, check_end_date, 
              check_start_date, check_end_date, check_start_date, check_end_date))
        
        if cur.fetchone():
            print("Error: Player already has a valid contract during this period.")
            return
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if start_date:
            update_fields.append("StartDate = %s")
            params.append(start_date)
        if end_date:
            update_fields.append("EndDate = %s")
            params.append(end_date)
        if salary:
            update_fields.append("Salary = %s")
            params.append(salary)
        
        # Add contract ID to params
        params.append(contract_id)
        
        if update_fields:
            query = f"UPDATE Contracts SET {', '.join(update_fields)} WHERE ContractID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Contract record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating contract record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve contracts for a specific player or club
    """
    try:
        # Get user choice
        print("Retrieve contracts by:")
        print("1. Player Name")
        print("2. Club Name")
        print("3. Generate Wage Bill for a club")
        choice = input("Enter choice: ")
        if choice == '3':
            # Get club name and validate
            print("Enter Club Name: ")
            club_name = input()
            cur.execute("SELECT SUM(Salary) FROM Clubs INNER JOIN Contracts ON Clubs.ClubID = Contracts.ClubID WHERE ClubName = %s", (club_name,))
            wage_bill = cur.fetchone()
            print(f"Wage bill for {club_name}: ${wage_bill['SUM(Salary)']:,.2f}")
            # assuming captaincy bonus is included in salary in contract.
            return

        if choice == '1':
            # Get player name and validate
            player_name = input("Enter Player Name: ")
            player_id = find_unique_player_by_name(cur, player_name)
            if not player_id:
                return
            
            # Retrieve contracts for player
            cur.execute("""
                SELECT * FROM Contracts 
                WHERE PlayerID = %s
            """, (player_id,))
            
            contracts = cur.fetchall()
            if contracts:
                print(f"Contracts for player: {player_name}")
                for contract in contracts:
                    print(f"Contract ID: {contract['ContractID']}, Club: {contract['ClubID']}, "
                          f"Start Date: {contract['StartDate']}, End Date: {contract['EndDate']}, "
                          f"Salary: ${contract['Salary']:,.2f}, Validity: {contract['Validity']}")
            else:
                print(f"No contracts found for player: {player_name}")
        
        elif choice == '2':
            # Get club name and validate
            club_name = input("Enter Club Name: ")
            club_id = find_unique_club_by_name(cur, club_name)
            if not club_id:
                return
            
            # Retrieve contracts for club
            cur.execute("""
                SELECT * FROM Contracts Left Join Players ON Contracts.PlayerID = Players.PlayerID 
                WHERE Contracts.ClubID = %s
            """, (club_id,))
            
            contracts = cur.fetchall()
            if contracts:
                print(f"Contracts for club: {club_name}")
                for contract in contracts:
                    print(f"Contract ID: {contract['ContractID']}, Player: {contract['PlayerName']}, "
                          f"Start Date: {contract['StartDate']}, End Date: {contract['EndDate']}, "
                          f"Salary: ${contract['Salary']:,.2f}, Validity: {contract['Validity']}")
            else:
                print(f"No contracts found for club: {club_name}")
        
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error retrieving contract records: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")