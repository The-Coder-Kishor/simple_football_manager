# managers.py
import pymysql

def addRecord(con, cur):
    """
    Add a new manager record
    """
    try:
        # Collect manager details
        manager_name = input("Enter Manager Name: ")
        
        # Validate and convert experience to integer
        while True:
            try:
                experience = int(input("Enter Years of Experience: "))
                break
            except ValueError:
                print("Please enter a valid integer for experience.")
        
        # Validate and convert salary to float
        while True:
            try:
                salary = float(input("Enter Salary: "))
                break
            except ValueError:
                print("Please enter a valid number for salary.")
        
        # Show available tactics for reference
        print("\nAvailable Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        # Get preferred tactic ID (optional)
        preferred_tactic_id = input("Enter Preferred Tactic ID (press enter to skip): ")
        preferred_tactic_id = int(preferred_tactic_id) if preferred_tactic_id else None
        
        # SQL query to insert manager
        query = """
        INSERT INTO Managers 
        (ManagerName, Experience, Salary, PreferredTacticID) 
        VALUES (%s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (manager_name, experience, salary, preferred_tactic_id))
        con.commit()
        
        print("Manager record added successfully!")
        print(f"New Manager: {manager_name}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding manager record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a manager record
    """
    try:
        # Retrieve and display managers to help user choose
        print("Current Managers:")
        cur.execute("SELECT ManagerID, ManagerName, Experience FROM Managers")
        managers = cur.fetchall()
        
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}, Experience: {manager['Experience']} years")
        
        # Get manager ID to delete
        while True:
            try:
                manager_id = int(input("Enter Manager ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer Manager ID.")
        
        # SQL query to delete manager
        query = "DELETE FROM Managers WHERE ManagerID = %s"
        
        # Execute the query
        cur.execute(query, (manager_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Manager with ID {manager_id} deleted successfully!")
        else:
            print(f"No manager found with ID {manager_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting manager record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a manager record
    """
    try:
        # Retrieve and display managers to help user choose
        print("Current Managers:")
        cur.execute("SELECT ManagerID, ManagerName, Experience FROM Managers")
        managers = cur.fetchall()
        
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}, Experience: {manager['Experience']} years")
        
        # Get manager ID to update
        while True:
            try:
                manager_id = int(input("Enter Manager ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer Manager ID.")
        
        # Collect new details (allow skipping)
        manager_name = input("Enter new Manager Name (press enter to skip): ")
        
        # Experience input with validation
        experience = input("Enter new Experience in years (press enter to skip): ")
        if experience:
            while not experience.isdigit():
                experience = input("Please enter a valid integer for Experience: ")
        
        # Salary input with validation
        salary = input("Enter new Salary (press enter to skip): ")
        if salary:
            while not salary.replace('.','',1).isdigit():
                salary = input("Please enter a valid number for Salary: ")
        
        # Show available tactics for reference
        print("\nAvailable Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        preferred_tactic_id = input("Enter new Preferred Tactic ID (press enter to skip, 'null' to remove): ")
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if manager_name:
            update_fields.append("ManagerName = %s")
            params.append(manager_name)
        if experience:
            update_fields.append("Experience = %s")
            params.append(int(experience))
        if salary:
            update_fields.append("Salary = %s")
            params.append(float(salary))
        if preferred_tactic_id:
            if preferred_tactic_id.lower() == 'null':
                update_fields.append("PreferredTacticID = NULL")
            else:
                update_fields.append("PreferredTacticID = %s")
                params.append(int(preferred_tactic_id))
        
        # Add manager ID to params
        params.append(manager_id)
        
        if update_fields:
            query = f"UPDATE Managers SET {', '.join(update_fields)} WHERE ManagerID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Manager record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating manager record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve manager records
    """
    try:
        # Option to retrieve all or specific manager
        choice = input("Retrieve (A)ll or (S)pecific manager? ").upper()
        
        if choice == 'A':
            # Retrieve all managers
            query = """
            SELECT m.*, t.Name as TacticName 
            FROM Managers m 
            LEFT JOIN Tactics t ON m.PreferredTacticID = t.TacticID
            """
            cur.execute(query)
        else:
            # Retrieve specific manager
            manager_id = int(input("Enter Manager ID: "))
            query = """
            SELECT m.*, t.Name as TacticName 
            FROM Managers m 
            LEFT JOIN Tactics t ON m.PreferredTacticID = t.TacticID 
            WHERE m.ManagerID = %s
            """
            cur.execute(query, (manager_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No managers found.")
        else:
            for manager in results:
                print("\nManager Details:")
                print(f"Manager ID: {manager['ManagerID']}")
                print(f"Name: {manager['ManagerName']}")
                print(f"Experience: {manager['Experience']} years")
                print(f"Salary: ${manager['Salary']:,.2f}")
                print(f"Preferred Tactic: {manager['TacticName'] if manager['TacticName'] else 'Not assigned'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving manager records: {e}")
    except ValueError:
        print("Please enter a valid Manager ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")