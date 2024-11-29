# injuryrecord.py
import pymysql
from datetime import datetime, date, timedelta

def addRecord(con, cur):
    """
    Add a new injury record
    """
    try:
        # Show available players with their current injury status
        print("Players and Their Current Injuries:")
        cur.execute("""
            SELECT p.PlayerID, p.PlayerName, c.ClubName,
                   MAX(i.InjuryDate) as LastInjury,
                   COUNT(i.InjuryID) as TotalInjuries
            FROM Players p
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            LEFT JOIN InjuryRecord i ON p.PlayerID = i.PlayerID
            GROUP BY p.PlayerID, p.PlayerName, c.ClubName
            ORDER BY p.PlayerName
        """)
        players = cur.fetchall()
        
        for player in players:
            club = player['ClubName'] if player['ClubName'] else 'No Club'
            last_injury = player['LastInjury'] if player['LastInjury'] else 'No injuries'
            print(f"\nID: {player['PlayerID']}, Name: {player['PlayerName']}")
            print(f"Club: {club}")
            print(f"Last Injury: {last_injury}")
            print(f"Total Injuries: {player['TotalInjuries']}")
        
        # Get player ID
        while True:
            try:
                player_id = int(input("\nEnter Player ID: "))
                # Verify player exists
                cur.execute("SELECT PlayerID FROM Players WHERE PlayerID = %s", (player_id,))
                if cur.fetchone():
                    break
                print("Invalid Player ID.")
            except ValueError:
                print("Please enter a valid integer Player ID.")
        
        # Injury date validation
        while True:
            injury_date = input("Enter Injury Date (YYYY-MM-DD): ")
            try:
                injury_date_obj = datetime.strptime(injury_date, '%Y-%m-%d').date()
                if injury_date_obj > date.today():
                    print("Injury date cannot be in the future.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Show standard severity levels
        print("\nStandard Severity Levels:")
        severities = ["Minor", "Moderate", "Severe", "Critical"]
        for sev in severities:
            print(sev)
        
        # Get severity
        while True:
            severity = input("\nEnter Injury Severity: ").capitalize()
            if severity in severities:
                break
            print("Please enter a valid severity level.")
        
        # Recurrence rate validation (0-100%)
        while True:
            try:
                recurrence_rate = float(input("Enter Recurrence Rate (0-100): "))
                if 0 <= recurrence_rate <= 100:
                    break
                print("Recurrence rate must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for recurrence rate.")
        
        # Check recovery prediction
        cur.execute("""
            SELECT DaysToRecovery 
            FROM RecoveryPrediction 
            WHERE Severity = %s AND RecurrenceRate = %s
        """, (severity, recurrence_rate))
        recovery = cur.fetchone()
        
        if recovery:
            predicted_recovery = injury_date_obj + timedelta(days=recovery['DaysToRecovery'])
            print(f"\nPredicted Recovery Date: {predicted_recovery}")
        
        # SQL query to insert injury record
        query = """
        INSERT INTO InjuryRecord 
        (PlayerID, InjuryDate, Severity, RecurrenceRate) 
        VALUES (%s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (player_id, injury_date, severity, recurrence_rate))
        con.commit()
        
        print("Injury record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding injury record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete an injury record
    """
    try:
        # Show current injury records
        print("Current Injury Records:")
        cur.execute("""
            SELECT i.InjuryID, p.PlayerName, i.InjuryDate, 
                   i.Severity, i.RecurrenceRate
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            ORDER BY i.InjuryDate DESC
        """)
        injuries = cur.fetchall()
        
        for injury in injuries:
            print(f"\nID: {injury['InjuryID']}")
            print(f"Player: {injury['PlayerName']}")
            print(f"Date: {injury['InjuryDate']}")
            print(f"Severity: {injury['Severity']}")
            print(f"Recurrence Rate: {injury['RecurrenceRate']}%")
        
        # Get injury ID to delete
        while True:
            try:
                injury_id = int(input("\nEnter Injury ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer Injury ID.")
        
        # SQL query to delete injury record
        query = "DELETE FROM InjuryRecord WHERE InjuryID = %s"
        
        # Execute the query
        cur.execute(query, (injury_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Injury record with ID {injury_id} deleted successfully!")
        else:
            print(f"No injury record found with ID {injury_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting injury record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update an injury record
    """
    try:
        # Show current injury records
        print("Current Injury Records:")
        cur.execute("""
            SELECT i.InjuryID, p.PlayerName, i.InjuryDate, 
                   i.Severity, i.RecurrenceRate
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            ORDER BY i.InjuryDate DESC
        """)
        injuries = cur.fetchall()
        
        for injury in injuries:
            print(f"\nID: {injury['InjuryID']}")
            print(f"Player: {injury['PlayerName']}")
            print(f"Date: {injury['InjuryDate']}")
            print(f"Severity: {injury['Severity']}")
            print(f"Recurrence Rate: {injury['RecurrenceRate']}%")
        
        # Get injury ID to update
        while True:
            try:
                injury_id = int(input("\nEnter Injury ID to update: "))
                # Verify injury record exists
                cur.execute("SELECT * FROM InjuryRecord WHERE InjuryID = %s", (injury_id,))
                if cur.fetchone():
                    break
                print("No injury record found with this ID.")
            except ValueError:
                print("Please enter a valid integer Injury ID.")
        
        # Get current record details
        cur.execute("""
            SELECT i.*, p.PlayerName 
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            WHERE i.InjuryID = %s
        """, (injury_id,))
        current = cur.fetchone()
        
        print(f"\nUpdating injury record for {current['PlayerName']}")
        print("Press Enter to keep current values:")
        
        # Injury date update
        injury_date = input(f"Enter new Injury Date (current: {current['InjuryDate']}, YYYY-MM-DD): ")
        if injury_date:
            try:
                injury_date_obj = datetime.strptime(injury_date, '%Y-%m-%d').date()
                if injury_date_obj > date.today():
                    print("Injury date cannot be in the future. Value not updated.")
                    injury_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                injury_date = None
        
        # Show standard severity levels
        print("\nStandard Severity Levels:")
        severities = ["Minor", "Moderate", "Severe", "Critical"]
        for sev in severities:
            print(sev)
        
        # Severity update
        severity = input(f"Enter new Severity (current: {current['Severity']}): ").capitalize()
        if severity and severity not in severities:
            print("Invalid severity level. Value not updated.")
            severity = None
        
        # Recurrence rate update
        recurrence_rate = input(f"Enter new Recurrence Rate (current: {current['RecurrenceRate']}%): ")
        if recurrence_rate:
            try:
                recurrence_rate = float(recurrence_rate)
                if not (0 <= recurrence_rate <= 100):
                    print("Recurrence rate must be between 0 and 100. Value not updated.")
                    recurrence_rate = None
            except ValueError:
                print("Invalid recurrence rate. Value not updated.")
                recurrence_rate = None
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if injury_date:
            update_fields.append("InjuryDate = %s")
            params.append(injury_date)
        if severity:
            update_fields.append("Severity = %s")
            params.append(severity)
        if recurrence_rate is not None:
            update_fields.append("RecurrenceRate = %s")
            params.append(recurrence_rate)
        
        if update_fields:
            # Add injury ID to params
            params.append(injury_id)
            
            query = f"UPDATE InjuryRecord SET {', '.join(update_fields)} WHERE InjuryID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            # Check updated recovery prediction if severity or recurrence rate changed
            if severity or recurrence_rate is not None:
                cur.execute("""
                    SELECT DaysToRecovery 
                    FROM RecoveryPrediction 
                    WHERE Severity = %s AND RecurrenceRate = %s
                """, (
                    severity if severity else current['Severity'],
                    recurrence_rate if recurrence_rate is not None else current['RecurrenceRate']
                ))
                recovery = cur.fetchone()
                if recovery:
                    injury_date_to_use = datetime.strptime(
                        injury_date if injury_date else str(current['InjuryDate']),
                        '%Y-%m-%d'
                    ).date()
                    predicted_recovery = injury_date_to_use + timedelta(days=recovery['DaysToRecovery'])
                    print(f"\nUpdated Predicted Recovery Date: {predicted_recovery}")
            
            print("Injury record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating injury record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve injury records
    """
    try:
        # Option to retrieve by player or all records
        choice = input("Retrieve injuries for (A)ll players or (S)pecific player? ").upper()
        
        if choice == 'A':
            # Option to filter by severity
            filter_choice = input("Filter by severity? (Y/N): ").upper()
            
            if filter_choice == 'Y':
                print("\nStandard Severity Levels:")
                severities = ["Minor", "Moderate", "Severe", "Critical"]
                for sev in severities:
                    print(sev)
                
                severity = input("\nEnter Severity: ").capitalize()
                query = """
                SELECT i.*, p.PlayerName, c.ClubName,
                       DATEDIFF(CURDATE(), i.InjuryDate) as DaysSinceInjury,
                       rp.DaysToRecovery
                FROM InjuryRecord i
                JOIN Players p ON i.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                LEFT JOIN RecoveryPrediction rp 
                    ON i.Severity = rp.Severity 
                    AND i.RecurrenceRate = rp.RecurrenceRate
                WHERE i.Severity = %s
                ORDER BY i.InjuryDate DESC
                """
                cur.execute(query, (severity,))
            else:
                query = """
                SELECT i.*, p.PlayerName, c.ClubName,
                       DATEDIFF(CURDATE(), i.InjuryDate) as DaysSinceInjury,
                       rp.DaysToRecovery
                FROM InjuryRecord i
                JOIN Players p ON i.PlayerID = p.PlayerID
                LEFT JOIN Clubs c ON p.ClubID = c.ClubID
                LEFT JOIN RecoveryPrediction rp 
                    ON i.Severity = rp.Severity 
                    AND i.RecurrenceRate = rp.RecurrenceRate
                ORDER BY i.InjuryDate DESC
                """
                cur.execute(query)
        else:
            # Get specific player ID
            player_id = int(input("Enter Player ID: "))
            query = """
            SELECT i.*, p.PlayerName, c.ClubName,
                   DATEDIFF(CURDATE(), i.InjuryDate) as DaysSinceInjury,
                   rp.DaysToRecovery
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            LEFT JOIN RecoveryPrediction rp 
                ON i.Severity = rp.Severity 
                AND i.RecurrenceRate = rp.RecurrenceRate
            WHERE i.PlayerID = %s
            ORDER BY i.InjuryDate DESC
            """
            cur.execute(query, (player_id,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No injury records found.")
        else:
            for injury in results:
                print("\nInjury Record Details:")
                print(f"Injury ID: {injury['InjuryID']}")
                print(f"Player: {injury['PlayerName']}")
                print(f"Club: {injury['ClubName'] if injury['ClubName'] else 'No Club'}")
                print(f"Injury Date: {injury['InjuryDate']}")
                print(f"Days Since Injury: {injury['DaysSinceInjury']}")
                print(f"Severity: {injury['Severity']}")
                print(f"Recurrence Rate: {injury['RecurrenceRate']}%")
                
                if injury['DaysToRecovery']:
                    predicted_recovery = injury['InjuryDate'] + timedelta(days=injury['DaysToRecovery'])
                    days_remaining = (predicted_recovery - date.today()).days
                    print(f"Predicted Recovery: {predicted_recovery}")
                    if days_remaining > 0:
                        print(f"Days Until Recovery: {days_remaining}")
                    else:
                        print("Recovery period has passed")
                
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving injury records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")