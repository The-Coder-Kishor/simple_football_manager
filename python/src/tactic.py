# tactic.py
import pymysql

def addRecord(con, cur):
    """
    Add a new tactic record
    """
    try:
        # Collect tactic details
        name = input("Enter Tactic Name: ")
        instruction = input("Enter Tactic Instructions: ")
        formation = input("Enter Formation (e.g., 4-4-2): ")
        style = input("Enter Playing Style: ")
        
        # Show available managers for reference
        print("\nAvailable Managers:")
        cur.execute("SELECT ManagerID, ManagerName FROM Managers")
        managers = cur.fetchall()
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
        
        # Get creator manager ID (optional)
        creator_manager_id = input("Enter Creator Manager ID (press enter to skip): ")
        creator_manager_id = int(creator_manager_id) if creator_manager_id else None
        
        # SQL query to insert tactic
        query = """
        INSERT INTO Tactics 
        (Name, Instruction, Formation, Style, CreatorManagerID) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (name, instruction, formation, style, creator_manager_id))
        con.commit()
        
        print("Tactic record added successfully!")
        print(f"New Tactic: {name} with formation {formation}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding tactic record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a tactic record
    """
    try:
        # Retrieve and display tactics to help user choose
        print("Current Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        # Get tactic ID to delete
        while True:
            try:
                tactic_id = int(input("Enter Tactic ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer Tactic ID.")
        
        # SQL query to delete tactic
        query = "DELETE FROM Tactics WHERE TacticID = %s"
        
        # Execute the query
        cur.execute(query, (tactic_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Tactic with ID {tactic_id} deleted successfully!")
        else:
            print(f"No tactic found with ID {tactic_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting tactic record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a tactic record
    """
    try:
        # Retrieve and display tactics to help user choose
        print("Current Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        # Get tactic ID to update
        while True:
            try:
                tactic_id = int(input("Enter Tactic ID to update: "))
                break
            except ValueError:
                print("Please enter a valid integer Tactic ID.")
        
        # Collect new details (allow skipping)
        name = input("Enter new Tactic Name (press enter to skip): ")
        instruction = input("Enter new Instructions (press enter to skip): ")
        formation = input("Enter new Formation (press enter to skip): ")
        style = input("Enter new Style (press enter to skip): ")
        
        # Show available managers for reference
        print("\nAvailable Managers:")
        cur.execute("SELECT ManagerID, ManagerName FROM Managers")
        managers = cur.fetchall()
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
        
        creator_manager_id = input("Enter new Creator Manager ID (press enter to skip): ")
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if name:
            update_fields.append("Name = %s")
            params.append(name)
        if instruction:
            update_fields.append("Instruction = %s")
            params.append(instruction)
        if formation:
            update_fields.append("Formation = %s")
            params.append(formation)
        if style:
            update_fields.append("Style = %s")
            params.append(style)
        if creator_manager_id:
            update_fields.append("CreatorManagerID = %s")
            params.append(int(creator_manager_id))
        
        # Add tactic ID to params
        params.append(tactic_id)
        
        if update_fields:
            query = f"UPDATE Tactics SET {', '.join(update_fields)} WHERE TacticID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Tactic record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating tactic record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve tactic records
    """
    try:
        # Option to retrieve all or specific tactic
        choice = input("Retrieve (A)ll or (S)pecific tactic? ").upper()
        
        if choice == 'A':
            # Retrieve all tactics
            query = """
            SELECT t.*, m.ManagerName 
            FROM Tactics t 
            LEFT JOIN Managers m ON t.CreatorManagerID = m.ManagerID
            """
            cur.execute(query)
        else:
            # Retrieve specific tactic
            tactic_id = int(input("Enter Tactic ID: "))
            query = """
            SELECT t.*, m.ManagerName 
            FROM Tactics t 
            LEFT JOIN Managers m ON t.CreatorManagerID = m.ManagerID 
            WHERE t.TacticID = %s
            """
            cur.execute(query, (tactic_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No tactics found.")
        else:
            for tactic in results:
                print("\nTactic Details:")
                print(f"Tactic ID: {tactic['TacticID']}")
                print(f"Name: {tactic['Name']}")
                print(f"Instructions: {tactic['Instruction']}")
                print(f"Formation: {tactic['Formation']}")
                print(f"Style: {tactic['Style']}")
                print(f"Creator Manager: {tactic['ManagerName'] if tactic['ManagerName'] else 'Not assigned'}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving tactic records: {e}")
    except ValueError:
        print("Please enter a valid Tactic ID.")
    except Exception as e:
        print(f"Unexpected error: {e}")