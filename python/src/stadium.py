# stadium.py
import pymysql

def addRecord(con, cur):
    """
    Add a new stadium record
    """
    try:
        stadium_name = input("Enter Stadium Name: ")
        city = input("Enter City: ")
        
        while True:
            try:
                capacity = int(input("Enter Stadium Capacity: "))
                break
            except ValueError:
                print("Please enter a valid integer for capacity.")
        
        while True:
            try:
                ticket_fare = float(input("Enter Ticket Fare: "))
                break
            except ValueError:
                print("Please enter a valid number for ticket fare.")
        
        query = """
        INSERT INTO Stadiums 
        (StadiumName, City, Capacity, TicketFare) 
        VALUES (%s, %s, %s, %s)
        """
        
        cur.execute(query, (stadium_name, city, capacity, ticket_fare))
        con.commit()
        
        print("Stadium record added successfully!")
        print(f"New Stadium: {stadium_name} in {city}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding stadium record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def find_stadium(cur, name=None, city=None):
    """
    Helper function to find stadium by name and/or city
    """
    conditions = []
    params = []
    
    if name:
        conditions.append("StadiumName = %s")
        params.append(name)
    if city:
        conditions.append("City = %s")
        params.append(city)
    
    if conditions:
        query = f"SELECT * FROM Stadiums WHERE {' AND '.join(conditions)}"
        cur.execute(query, params)
        return cur.fetchall()
    return []

def deleteRecord(con, cur):
    """
    Delete a stadium record
    """
    try:
        name = input("Enter Stadium Name (press enter to skip): ")
        city = input("Enter City (press enter to skip): ")
        
        if not name and not city:
            print("Please provide at least stadium name or city.")
            return
            
        stadiums = find_stadium(cur, name, city)
        
        if not stadiums:
            print("No matching stadium found.")
            return
            
        if len(stadiums) > 1:
            print("Multiple stadiums found:")
            for stadium in stadiums:
                print(f"Name: {stadium['StadiumName']}, City: {stadium['City']}")
            confirm = input("Do you want to delete all these stadiums? (yes/no): ").lower()
            if confirm != 'yes':
                return
        
        query = "DELETE FROM Stadiums WHERE "
        conditions = []
        params = []
        
        if name:
            conditions.append("StadiumName = %s")
            params.append(name)
        if city:
            conditions.append("City = %s")
            params.append(city)
            
        query += " AND ".join(conditions)
        
        cur.execute(query, params)
        con.commit()
        print(f"Stadium(s) deleted successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting stadium record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a stadium record
    """
    try:
        search_name = input("Enter Stadium Name to update: ")
        search_city = input("Enter City to update (press enter to skip): ")
        
        if not search_name and not search_city:
            print("Please provide at least stadium name or city.")
            return
            
        stadiums = find_stadium(cur, search_name, search_city)
        
        if not stadiums:
            print("No matching stadium found.")
            return
            
        if len(stadiums) > 1:
            print("Multiple stadiums found. Please be more specific.")
            return
            
        # Collect new details
        stadium_name = input("Enter new Stadium Name (press enter to skip): ")
        city = input("Enter new City (press enter to skip): ")
        
        capacity = input("Enter new Capacity (press enter to skip): ")
        if capacity:
            while not capacity.isdigit():
                capacity = input("Please enter a valid integer for Capacity: ")
        
        ticket_fare = input("Enter new Ticket Fare (press enter to skip): ")
        if ticket_fare:
            while not ticket_fare.replace('.','',1).isdigit():
                ticket_fare = input("Please enter a valid number for Ticket Fare: ")
        
        update_fields = []
        params = []
        
        if stadium_name:
            update_fields.append("StadiumName = %s")
            params.append(stadium_name)
        if city:
            update_fields.append("City = %s")
            params.append(city)
        if capacity:
            update_fields.append("Capacity = %s")
            params.append(int(capacity))
        if ticket_fare:
            update_fields.append("TicketFare = %s")
            params.append(float(ticket_fare))
        
        if update_fields:
            query = f"UPDATE Stadiums SET {', '.join(update_fields)} WHERE StadiumName = %s"
            params.append(search_name)
            if search_city:
                query += " AND City = %s"
                params.append(search_city)
                
            cur.execute(query, params)
            con.commit()
            print("Stadium record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating stadium record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve stadium records
    """
    try:
        choice = input("Retrieve (A)ll or (S)pecific stadium? ").upper()
        
        if choice == 'A':
            query = "SELECT * FROM Stadiums"
            cur.execute(query)
            results = cur.fetchall()
        else:
            name = input("Enter Stadium Name (press enter to skip): ")
            city = input("Enter City (press enter to skip): ")
            results = find_stadium(cur, name, city)
        
        if not results:
            print("No stadiums found.")
        else:
            for stadium in results:
                print("\nStadium Details:")
                print(f"Stadium Name: {stadium['StadiumName']}")
                print(f"City: {stadium['City']}")
                print(f"Capacity: {stadium['Capacity']}")
                print(f"Ticket Fare: ${stadium['TicketFare']:.2f}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving stadium records: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")