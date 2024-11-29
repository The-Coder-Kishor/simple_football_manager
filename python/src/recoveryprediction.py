# recoveryprediction.py
import pymysql

def addRecord(con, cur):
    """
    Add a new recovery prediction record
    """
    try:
        # Show current recovery predictions
        print("Current Recovery Predictions:")
        cur.execute("""
            SELECT Severity, RecurrenceRate, DaysToRecovery 
            FROM RecoveryPrediction 
            ORDER BY Severity, RecurrenceRate
        """)
        predictions = cur.fetchall()
        
        for pred in predictions:
            print(f"Severity: {pred['Severity']}, "
                  f"Recurrence Rate: {pred['RecurrenceRate']}%, "
                  f"Recovery Days: {pred['DaysToRecovery']}")
        
        # Show standard severity levels
        print("\nStandard Severity Levels:")
        severities = ["Minor", "Moderate", "Severe", "Critical"]
        for sev in severities:
            print(sev)
        
        # Get severity
        while True:
            severity = input("\nEnter Severity: ").capitalize()
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
        
        # Check if combination already exists
        cur.execute("""
            SELECT * FROM RecoveryPrediction 
            WHERE Severity = %s AND RecurrenceRate = %s
        """, (severity, recurrence_rate))
        
        if cur.fetchone():
            print("This severity and recurrence rate combination already exists.")
            return
        
        # Days to recovery validation
        while True:
            try:
                days_to_recovery = int(input("Enter Days to Recovery: "))
                if days_to_recovery > 0:
                    break
                print("Days to recovery must be greater than 0.")
            except ValueError:
                print("Please enter a valid integer for days to recovery.")
        
        # SQL query to insert recovery prediction
        query = """
        INSERT INTO RecoveryPrediction 
        (Severity, RecurrenceRate, DaysToRecovery) 
        VALUES (%s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (severity, recurrence_rate, days_to_recovery))
        con.commit()
        
        print("Recovery prediction record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding recovery prediction record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a recovery prediction record
    """
    try:
        # Show current recovery predictions
        print("Current Recovery Predictions:")
        cur.execute("""
            SELECT Severity, RecurrenceRate, DaysToRecovery 
            FROM RecoveryPrediction 
            ORDER BY Severity, RecurrenceRate
        """)
        predictions = cur.fetchall()
        
        for pred in predictions:
            print(f"\nSeverity: {pred['Severity']}")
            print(f"Recurrence Rate: {pred['RecurrenceRate']}%")
            print(f"Days to Recovery: {pred['DaysToRecovery']}")
        
        # Get severity and recurrence rate to identify record
        print("\nEnter details to delete record:")
        severity = input("Enter Severity: ").capitalize()
        
        while True:
            try:
                recurrence_rate = float(input("Enter Recurrence Rate: "))
                if 0 <= recurrence_rate <= 100:
                    break
                print("Recurrence rate must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for recurrence rate.")
        
        # Check if record is referenced in InjuryRecord
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM InjuryRecord 
            WHERE Severity = %s AND RecurrenceRate = %s
        """, (severity, recurrence_rate))
        
        if cur.fetchone()['count'] > 0:
            print("Cannot delete: This prediction is referenced in injury records.")
            return
        
        # SQL query to delete recovery prediction
        query = """
        DELETE FROM RecoveryPrediction 
        WHERE Severity = %s AND RecurrenceRate = %s
        """
        
        # Execute the query
        cur.execute(query, (severity, recurrence_rate))
        
        if cur.rowcount > 0:
            con.commit()
            print("Recovery prediction record deleted successfully!")
        else:
            print("No matching recovery prediction found.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting recovery prediction record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a recovery prediction record
    """
    try:
        # Show current recovery predictions
        print("Current Recovery Predictions:")
        cur.execute("""
            SELECT Severity, RecurrenceRate, DaysToRecovery 
            FROM RecoveryPrediction 
            ORDER BY Severity, RecurrenceRate
        """)
        predictions = cur.fetchall()
        
        for pred in predictions:
            print(f"\nSeverity: {pred['Severity']}")
            print(f"Recurrence Rate: {pred['RecurrenceRate']}%")
            print(f"Days to Recovery: {pred['DaysToRecovery']}")
        
        # Get severity and recurrence rate to identify record
        print("\nEnter details to identify record:")
        severity = input("Enter Severity: ").capitalize()
        
        while True:
            try:
                recurrence_rate = float(input("Enter Recurrence Rate: "))
                if 0 <= recurrence_rate <= 100:
                    break
                print("Recurrence rate must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number for recurrence rate.")
        
        # Verify record exists
        cur.execute("""
            SELECT * FROM RecoveryPrediction 
            WHERE Severity = %s AND RecurrenceRate = %s
        """, (severity, recurrence_rate))
        
        current = cur.fetchone()
        if not current:
            print("No matching recovery prediction found.")
            return
        
        # Get new days to recovery
        while True:
            try:
                days_to_recovery = int(input(f"Enter new Days to Recovery (current: {current['DaysToRecovery']}): "))
                if days_to_recovery > 0:
                    break
                print("Days to recovery must be greater than 0.")
            except ValueError:
                print("Please enter a valid integer for days to recovery.")
        
        # SQL query to update recovery prediction
        query = """
        UPDATE RecoveryPrediction 
        SET DaysToRecovery = %s 
        WHERE Severity = %s AND RecurrenceRate = %s
        """
        
        # Execute the query
        cur.execute(query, (days_to_recovery, severity, recurrence_rate))
        con.commit()
        
        print("Recovery prediction record updated successfully!")
        
        # Show affected injury records
        cur.execute("""
            SELECT p.PlayerName, i.InjuryDate
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            WHERE i.Severity = %s AND i.RecurrenceRate = %s
        """, (severity, recurrence_rate))
        
        affected = cur.fetchall()
        if affected:
            print("\nAffected Injury Records:")
            for record in affected:
                print(f"Player: {record['PlayerName']}, Injury Date: {record['InjuryDate']}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating recovery prediction record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve recovery prediction records
    """
    try:
        # Option to retrieve all or filter by severity
        choice = input("Retrieve (A)ll predictions or filter by (S)everity? ").upper()
        
        if choice == 'S':
            # Show standard severity levels
            print("\nStandard Severity Levels:")
            severities = ["Minor", "Moderate", "Severe", "Critical"]
            for sev in severities:
                print(sev)
            
            severity = input("\nEnter Severity: ").capitalize()
            query = """
            SELECT rp.*, 
                   COUNT(i.InjuryID) as TimesUsed,
                   AVG(DATEDIFF(CURDATE(), i.InjuryDate)) as AvgDaysSinceInjury
            FROM RecoveryPrediction rp
            LEFT JOIN InjuryRecord i 
                ON rp.Severity = i.Severity 
                AND rp.RecurrenceRate = i.RecurrenceRate
            WHERE rp.Severity = %s
            GROUP BY rp.Severity, rp.RecurrenceRate
            ORDER BY rp.RecurrenceRate
            """
            cur.execute(query, (severity,))
        else:
            query = """
            SELECT rp.*, 
                   COUNT(i.InjuryID) as TimesUsed,
                   AVG(DATEDIFF(CURDATE(), i.InjuryDate)) as AvgDaysSinceInjury
            FROM RecoveryPrediction rp
            LEFT JOIN InjuryRecord i 
                ON rp.Severity = i.Severity 
                AND rp.RecurrenceRate = i.RecurrenceRate
            GROUP BY rp.Severity, rp.RecurrenceRate
            ORDER BY rp.Severity, rp.RecurrenceRate
            """
            cur.execute(query)
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No recovery predictions found.")
        else:
            current_severity = None
            for pred in results:
                if pred['Severity'] != current_severity:
                    current_severity = pred['Severity']
                    print(f"\n=== {current_severity} Severity ===")
                
                print(f"\nRecurrence Rate: {pred['RecurrenceRate']}%")
                print(f"Days to Recovery: {pred['DaysToRecovery']}")
                print(f"Times Used: {pred['TimesUsed']}")
                if pred['AvgDaysSinceInjury']:
                    print(f"Average Days Since Injury: {pred['AvgDaysSinceInjury']:.1f}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving recovery prediction records: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")