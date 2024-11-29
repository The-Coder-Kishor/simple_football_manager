# managernationality.py
import pymysql

def addRecord(con, cur):
    """
    Add a new manager nationality record
    """
    try:
        # Show available managers with their current nationalities
        print("Available Managers:")
        cur.execute("""
            SELECT m.ManagerID, m.ManagerName, 
                   GROUP_CONCAT(mn.Nationality) as CurrentNationalities,
                   c.ClubName
            FROM Managers m
            LEFT JOIN ManagerNationality mn ON m.ManagerID = mn.ManagerID
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            GROUP BY m.ManagerID, m.ManagerName, c.ClubName
            ORDER BY m.ManagerName
        """)
        managers = cur.fetchall()
        
        for manager in managers:
            nationalities = manager['CurrentNationalities'] if manager['CurrentNationalities'] else 'No nationalities'
            club = manager['ClubName'] if manager['ClubName'] else 'No Club'
            print(f"\nID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
            print(f"Current Club: {club}")
            print(f"Current Nationalities: {nationalities}")
        
        # Get manager ID
        while True:
            try:
                manager_id = int(input("\nEnter Manager ID: "))
                # Verify manager exists
                cur.execute("SELECT ManagerID FROM Managers WHERE ManagerID = %s", (manager_id,))
                if cur.fetchone():
                    break
                print("Manager ID not found. Please enter a valid ID.")
            except ValueError:
                print("Please enter a valid integer Manager ID.")
        
        # Get nationality
        nationality = input("Enter Nationality: ").strip().capitalize()
        while not nationality:
            print("Nationality cannot be empty.")
            nationality = input("Enter Nationality: ").strip().capitalize()
        
        # Check if this nationality already exists for the manager
        cur.execute("""
            SELECT * FROM ManagerNationality 
            WHERE ManagerID = %s AND Nationality = %s
        """, (manager_id, nationality))
        
        if cur.fetchone():
            print("This nationality is already registered for this manager.")
            return
        
        # SQL query to insert manager nationality
        query = """
        INSERT INTO ManagerNationality 
        (ManagerID, Nationality) 
        VALUES (%s, %s)
        """
        
        # Execute the query
        cur.execute(query, (manager_id, nationality))
        con.commit()
        
        print("Manager nationality record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding manager nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a manager nationality record
    """
    try:
        # Show current manager nationalities
        print("Current Manager Nationalities:")
        cur.execute("""
            SELECT mn.ManagerNationalityID, m.ManagerName, mn.Nationality,
                   c.ClubName
            FROM ManagerNationality mn
            JOIN Managers m ON mn.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            ORDER BY m.ManagerName, mn.Nationality
        """)
        nationalities = cur.fetchall()
        
        for nationality in nationalities:
            club = nationality['ClubName'] if nationality['ClubName'] else 'No Club'
            print(f"\nID: {nationality['ManagerNationalityID']}")
            print(f"Manager: {nationality['ManagerName']}")
            print(f"Club: {club}")
            print(f"Nationality: {nationality['Nationality']}")
        
        # Get nationality ID to delete
        while True:
            try:
                nationality_id = int(input("\nEnter Manager Nationality ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # SQL query to delete manager nationality
        query = "DELETE FROM ManagerNationality WHERE ManagerNationalityID = %s"
        
        # Execute the query
        cur.execute(query, (nationality_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Manager nationality with ID {nationality_id} deleted successfully!")
        else:
            print(f"No nationality record found with ID {nationality_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting manager nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a manager nationality record
    """
    try:
        # Show current manager nationalities
        print("Current Manager Nationalities:")
        cur.execute("""
            SELECT mn.ManagerNationalityID, m.ManagerName, mn.Nationality,
                   c.ClubName
            FROM ManagerNationality mn
            JOIN Managers m ON mn.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            ORDER BY m.ManagerName, mn.Nationality
        """)
        nationalities = cur.fetchall()
        
        for nationality in nationalities:
            club = nationality['ClubName'] if nationality['ClubName'] else 'No Club'
            print(f"\nID: {nationality['ManagerNationalityID']}")
            print(f"Manager: {nationality['ManagerName']}")
            print(f"Club: {club}")
            print(f"Nationality: {nationality['Nationality']}")
        
        # Get nationality ID to update
        while True:
            try:
                nationality_id = int(input("\nEnter Manager Nationality ID to update: "))
                # Verify record exists
                cur.execute("SELECT * FROM ManagerNationality WHERE ManagerNationalityID = %s", (nationality_id,))
                if cur.fetchone():
                    break
                print("No nationality record found with this ID.")
            except ValueError:
                print("Please enter a valid integer ID.")
        
        # Show available managers
        print("\nAvailable Managers:")
        cur.execute("""
            SELECT m.ManagerID, m.ManagerName, 
                   GROUP_CONCAT(mn.Nationality) as CurrentNationalities,
                   c.ClubName
            FROM Managers m
            LEFT JOIN ManagerNationality mn ON m.ManagerID = mn.ManagerID
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            GROUP BY m.ManagerID, m.ManagerName, c.ClubName
        """)
        managers = cur.fetchall()
        
        for manager in managers:
            nationalities = manager['CurrentNationalities'] if manager['CurrentNationalities'] else 'No nationalities'
            club = manager['ClubName'] if manager['ClubName'] else 'No Club'
            print(f"\nID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
            print(f"Current Club: {club}")
            print(f"Current Nationalities: {nationalities}")
        
        # Get new manager ID (optional)
        manager_id = input("\nEnter new Manager ID (press enter to skip): ")
        if manager_id:
            try:
                manager_id = int(manager_id)
                # Verify manager exists
                cur.execute("SELECT ManagerID FROM Managers WHERE ManagerID = %s", (manager_id,))
                if not cur.fetchone():
                    print("Manager ID not found. Manager not updated.")
                    manager_id = None
            except ValueError:
                print("Invalid manager ID. Manager not updated.")
                manager_id = None
        
        # Get new nationality (optional)
        nationality = input("Enter new Nationality (press enter to skip): ").strip()
        if nationality:
            nationality = nationality.capitalize()
            # Check for duplicate nationality if manager is being updated
            if manager_id:
                cur.execute("""
                    SELECT * FROM ManagerNationality 
                    WHERE ManagerID = %s AND Nationality = %s 
                    AND ManagerNationalityID != %s
                """, (manager_id, nationality, nationality_id))
                if cur.fetchone():
                    print("This nationality is already registered for this manager.")
                    return
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if manager_id:
            update_fields.append("ManagerID = %s")
            params.append(manager_id)
        if nationality:
            update_fields.append("Nationality = %s")
            params.append(nationality)
        
        if update_fields:
            # Add nationality ID to params
            params.append(nationality_id)
            
            query = f"UPDATE ManagerNationality SET {', '.join(update_fields)} WHERE ManagerNationalityID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Manager nationality record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating manager nationality record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve manager nationality records
    """
    try:
        # Option to retrieve all or specific manager nationalities
        choice = input("Retrieve nationalities for (A)ll managers or (S)pecific manager? ").upper()
        
        if choice == 'A':
            # Option to group by nationality
            group_choice = input("Group by (N)ationality or (M)anager? ").upper()
            
            if group_choice == 'N':
                query = """
                SELECT mn.Nationality,
                       GROUP_CONCAT(m.ManagerName ORDER BY m.ManagerName) as Managers,
                       COUNT(*) as ManagerCount
                FROM ManagerNationality mn
                JOIN Managers m ON mn.ManagerID = m.ManagerID
                GROUP BY mn.Nationality
                ORDER BY mn.Nationality
                """
                cur.execute(query)
                
                results = cur.fetchall()
                if results:
                    print("\nManagers by Nationality:")
                    for result in results:
                        print(f"\nNationality: {result['Nationality']}")
                        print(f"Number of Managers: {result['ManagerCount']}")
                        print(f"Managers: {result['Managers']}")
                
            else:
                query = """
                SELECT m.ManagerID, m.ManagerName,
                       GROUP_CONCAT(mn.Nationality ORDER BY mn.Nationality) as Nationalities,
                       c.ClubName
                FROM Managers m
                LEFT JOIN ManagerNationality mn ON m.ManagerID = mn.ManagerID
                LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
                GROUP BY m.ManagerID, m.ManagerName, c.ClubName
                ORDER BY m.ManagerName
                """
                cur.execute(query)
                
                results = cur.fetchall()
                if results:
                    print("\nManager Nationalities:")
                    for result in results:
                        print(f"\nManager: {result['ManagerName']}")
                        club = result['ClubName'] if result['ClubName'] else 'No Club'
                        print(f"Current Club: {club}")
                        nationalities = result['Nationalities'] if result['Nationalities'] else 'None registered'
                        print(f"Nationalities: {nationalities}")
        
        else:
            # Get specific manager ID
            manager_id = int(input("Enter Manager ID: "))
            query = """
            SELECT m.ManagerName, m.Experience,
                   GROUP_CONCAT(mn.Nationality ORDER BY mn.Nationality) as Nationalities,
                   c.ClubName
            FROM Managers m
            LEFT JOIN ManagerNationality mn ON m.ManagerID = mn.ManagerID
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            WHERE m.ManagerID = %s
            GROUP BY m.ManagerName, m.Experience, c.ClubName
            """
            cur.execute(query, (manager_id,))
            
            result = cur.fetchone()
            if result:
                print("\nManager Details:")
                print(f"Name: {result['ManagerName']}")
                print(f"Experience: {result['Experience']} years")
                club = result['ClubName'] if result['ClubName'] else 'No Club'
                print(f"Current Club: {club}")
                nationalities = result['Nationalities'] if result['Nationalities'] else 'None registered'
                print(f"Nationalities: {nationalities}")
            else:
                print("Manager not found.")
    
    except pymysql.Error as e:
        print(f"Error retrieving manager nationality records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")