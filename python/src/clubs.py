import pymysql
from datetime import datetime

def search_clubs_by_name(cur, name):
    """
    Search for clubs by name and return matching records
    
    Args:
        cur (pymysql.cursors.Cursor): Database cursor
        name (str): Partial or full club name to search
    
    Returns:
        list: List of matching club records
    """
    query = """
    SELECT ClubID, ClubName, Prestige 
    FROM Clubs 
    WHERE ClubName LIKE %s
    """
    cur.execute(query, (f'%{name}%',))
    return cur.fetchall()

def addRecord(con, cur):
    """
    Add a new club record
    """
    try:
        # Collect club details
        club_name = input("Enter Club Name: ")
        
        # Date validation
        while True:
            foundation_date = input("Enter Foundation Date (YYYY-MM-DD): ")
            try:
                datetime.strptime(foundation_date, '%Y-%m-%d')
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Validate and convert prestige to integer (1-5 scale)
        while True:
            try:
                prestige = int(input("Enter Prestige (1-5): "))
                if 1 <= prestige <= 5:
                    break
                print("Prestige must be between 1 and 5.")
            except ValueError:
                print("Please enter a valid integer for prestige.")
        
        # Validate and convert budget to float
        while True:
            try:
                budget = float(input("Enter Budget: "))
                break
            except ValueError:
                print("Please enter a valid number for budget.")
        
        # Show available stadiums for reference
        print("\nAvailable Stadiums:")
        cur.execute("SELECT StadiumID, StadiumName, City FROM Stadiums")
        stadiums = cur.fetchall()
        for stadium in stadiums:
            print(f"ID: {stadium['StadiumID']}, Name: {stadium['StadiumName']}, City: {stadium['City']}")
        
        # Get home stadium ID (optional)
        home_stadium_id = input("Enter Home Stadium ID (press enter to skip): ")
        home_stadium_id = int(home_stadium_id) if home_stadium_id else None
        
        # Show available managers for reference
        print("\nAvailable Managers:")
        cur.execute("SELECT ManagerID, ManagerName FROM Managers")
        managers = cur.fetchall()
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
        
        # Get manager ID (optional)
        manager_id = input("Enter Manager ID (press enter to skip): ")
        manager_id = int(manager_id) if manager_id else None
        
        # SQL query to insert club
        query = """
        INSERT INTO Clubs 
        (ClubName, FoundationDate, Prestige, Budget, HomeStadiumID, ManagerID) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (club_name, foundation_date, prestige, budget, home_stadium_id, manager_id))
        con.commit()
        
        print("Club record added successfully!")
        print(f"New Club: {club_name}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding club record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a club record by name
    """
    try:
        # Get club name to search
        club_name = input("Enter Club Name (or part of name) to delete: ")
        
        # Search for clubs
        clubs = search_clubs_by_name(cur, club_name)
        
        if not clubs:
            print(f"No clubs found matching '{club_name}'.")
            return
        
        # Display matching clubs
        print("Matching Clubs:")
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}, Prestige: {club['Prestige']}")
        
        # Get club ID to delete
        while True:
            try:
                club_id = int(input("Enter Club ID to delete: "))
                # Verify the ID is from the search results
                if any(club['ClubID'] == club_id for club in clubs):
                    break
                else:
                    print("Please choose a Club ID from the displayed list.")
            except ValueError:
                print("Please enter a valid integer Club ID.")
        
        # SQL query to delete club
        query = "DELETE FROM Clubs WHERE ClubID = %s"
        
        # Execute the query
        cur.execute(query, (club_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Club with ID {club_id} deleted successfully!")
        else:
            print(f"No club found with ID {club_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting club record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a club record by name
    """
    try:
        # Get club name to search
        club_name = input("Enter Club Name (or part of name) to update: ")
        
        # Search for clubs
        clubs = search_clubs_by_name(cur, club_name)
        
        if not clubs:
            print(f"No clubs found matching '{club_name}'.")
            return
        
        # Display matching clubs
        print("Matching Clubs:")
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}, Prestige: {club['Prestige']}")
        
        # Get club ID to update
        while True:
            try:
                club_id = int(input("Enter Club ID to update: "))
                # Verify the ID is from the search results
                if any(club['ClubID'] == club_id for club in clubs):
                    break
                else:
                    print("Please choose a Club ID from the displayed list.")
            except ValueError:
                print("Please enter a valid integer Club ID.")
        
        # Collect new details (allow skipping)
        new_club_name = input("Enter new Club Name (press enter to skip): ")
        
        # Foundation date validation
        foundation_date = input("Enter new Foundation Date (YYYY-MM-DD) (press enter to skip): ")
        if foundation_date:
            while True:
                try:
                    datetime.strptime(foundation_date, '%Y-%m-%d')
                    break
                except ValueError:
                    foundation_date = input("Please enter a valid date in YYYY-MM-DD format: ")
        
        # Prestige validation
        prestige = input("Enter new Prestige (1-5) (press enter to skip): ")
        if prestige:
            while True:
                try:
                    prestige = int(prestige)
                    if 1 <= prestige <= 5:
                        break
                    prestige = input("Prestige must be between 1 and 5: ")
                except ValueError:
                    prestige = input("Please enter a valid integer for Prestige: ")
        
        # Budget validation
        budget = input("Enter new Budget (press enter to skip): ")
        if budget:
            while True:
                try:
                    budget = float(budget)
                    break
                except ValueError:
                    budget = input("Please enter a valid number for Budget: ")
        
        # Show available stadiums and managers
        print("\nAvailable Stadiums:")
        cur.execute("SELECT StadiumID, StadiumName, City FROM Stadiums")
        stadiums = cur.fetchall()
        for stadium in stadiums:
            print(f"ID: {stadium['StadiumID']}, Name: {stadium['StadiumName']}, City: {stadium['City']}")
        
        print("\nAvailable Managers:")
        cur.execute("SELECT ManagerID, ManagerName FROM Managers")
        managers = cur.fetchall()
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
        
        home_stadium_id = input("Enter new Home Stadium ID (press enter to skip, 'null' to remove): ")
        manager_id = input("Enter new Manager ID (press enter to skip, 'null' to remove): ")
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if new_club_name:
            update_fields.append("ClubName = %s")
            params.append(new_club_name)
        if foundation_date:
            update_fields.append("FoundationDate = %s")
            params.append(foundation_date)
        if prestige:
            update_fields.append("Prestige = %s")
            params.append(prestige)
        if budget:
            update_fields.append("Budget = %s")
            params.append(budget)
        if home_stadium_id:
            if home_stadium_id.lower() == 'null':
                update_fields.append("HomeStadiumID = NULL")
            else:
                update_fields.append("HomeStadiumID = %s")
                params.append(int(home_stadium_id))
        if manager_id:
            if manager_id.lower() == 'null':
                update_fields.append("ManagerID = NULL")
            else:
                update_fields.append("ManagerID = %s")
                params.append(int(manager_id))
        
        # Add club ID to params
        params.append(club_id)
        
        if update_fields:
            query = f"UPDATE Clubs SET {', '.join(update_fields)} WHERE ClubID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Club record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating club record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve club records by name
    """
    try:
        # Option to retrieve all or specific club
        choice = input("Retrieve (A)ll or (S)pecific club? ").upper()
        
        if choice == 'A':
            # Retrieve all clubs with related information
            query = """
            SELECT c.*, s.StadiumName, s.City as StadiumCity, m.ManagerName 
            FROM Clubs c 
            LEFT JOIN Stadiums s ON c.HomeStadiumID = s.StadiumID 
            LEFT JOIN Managers m ON c.ManagerID = m.ManagerID
            """
            cur.execute(query)
        else:
            # Retrieve specific club by name
            club_name = input("Enter Club Name (or part of name): ")
            query = """
            SELECT c.*, s.StadiumName, s.City as StadiumCity, m.ManagerName 
            FROM Clubs c 
            LEFT JOIN Stadiums s ON c.HomeStadiumID = s.StadiumID 
            LEFT JOIN Managers m ON c.ManagerID = m.ManagerID 
            WHERE c.ClubName LIKE %s
            """
            cur.execute(query, (f'%{club_name}%',))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No clubs found.")
        else:
            for club in results:
                print("\nClub Details:")
                print(f"Club ID: {club['ClubID']}")
                print(f"Name: {club['ClubName']}")
                print(f"Foundation Date: {club['FoundationDate']}")
                print(f"Prestige: {club['Prestige']}")
                print(f"Budget: ${club['Budget']:,.2f}")
                print(f"Home Stadium: {club['StadiumName'] if club['StadiumName'] else 'Not assigned'}")
                if club['StadiumName']:
                    print(f"Stadium City: {club['StadiumCity']}")
                print(f"Manager: {club['ManagerName'] if club['ManagerName'] else 'Not assigned'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving club records: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")