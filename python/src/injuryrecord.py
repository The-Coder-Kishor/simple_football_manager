# injuryrecord.py
import pymysql
from datetime import datetime, date, timedelta

def addRecord(con, cur):
    """
    Add a new injury record using player name
    """
    try:
        player_name = input("\nEnter Player Name: ")
        
        # Find player ID from name
        cur.execute("""
            SELECT PlayerID, PlayerName, ClubName 
            FROM Players p 
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID 
            WHERE PlayerName LIKE %s
        """, (f"%{player_name}%",))
        players = cur.fetchall()
        
        if not players:
            print("No player found with that name.")
            return
        elif len(players) > 1:
            print("\nMultiple players found:")
            for idx, player in enumerate(players, 1):
                club = player['ClubName'] if player['ClubName'] else 'No Club'
                print(f"{idx}. {player['PlayerName']} ({club})")
            while True:
                try:
                    choice = int(input("Select player number: ")) - 1
                    if 0 <= choice < len(players):
                        player_id = players[choice]['PlayerID']
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            player_id = players[0]['PlayerID']

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

        # Get severity
        severities = ["Mild", "Moderate", "Severe"]
        while True:
            severity = input("Enter Injury Severity (Minor/Moderate/Severe/Critical): ").capitalize()
            if severity in severities:
                break
            print("Please enter a valid severity level.")

        # Recurrence rate validation
        while True:
            try:
                recurrence_rate = float(input("Enter Recurrence Rate (0-100): "))
                if 0 <= recurrence_rate <= 100:
                    break
                print("Recurrence rate must be between 0 and 100.")
            except ValueError:
                print("Please enter a valid number.")

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

        # Insert injury record
        cur.execute("""
            INSERT INTO InjuryRecord 
            (PlayerID, InjuryDate, Severity, RecurrenceRate) 
            VALUES (%s, %s, %s, %s)
        """, (player_id, injury_date, severity, recurrence_rate))
        con.commit()
        
        print("Injury record added successfully!")

    except pymysql.Error as e:
        con.rollback()
        print(f"Database error: {e}")
    except Exception as e:
        con.rollback()
        print(f"Error: {e}")

def deleteRecord(con, cur):
    """
    Delete an injury record using player name
    """
    try:
        player_name = input("\nEnter Player Name: ")
        
        # Show injuries for specific player
        cur.execute("""
            SELECT i.InjuryID, p.PlayerName, i.InjuryDate, i.Severity, c.ClubName
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerName LIKE %s
            ORDER BY i.InjuryDate DESC
        """, (f"%{player_name}%",))
        
        injuries = cur.fetchall()
        if not injuries:
            print("No injuries found for this player.")
            return
            
        print("\nInjuries found:")
        for idx, injury in enumerate(injuries, 1):
            club = injury['ClubName'] if injury['ClubName'] else 'No Club'
            print(f"{idx}. Date: {injury['InjuryDate']}, Severity: {injury['Severity']}, Club: {club}")
        
        while True:
            try:
                choice = int(input("\nSelect injury number to delete: ")) - 1
                if 0 <= choice < len(injuries):
                    injury_id = injuries[choice]['InjuryID']
                    break
                print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

        # Delete the selected injury
        cur.execute("DELETE FROM InjuryRecord WHERE InjuryID = %s", (injury_id,))
        con.commit()
        print("Injury record deleted successfully!")

    except pymysql.Error as e:
        con.rollback()
        print(f"Database error: {e}")
    except Exception as e:
        con.rollback()
        print(f"Error: {e}")

def updateRecord(con, cur):
    """
    Update an injury record using player name
    """
    try:
        player_name = input("\nEnter Player Name: ")
        
        # Show injuries for specific player
        cur.execute("""
            SELECT i.*, p.PlayerName, c.ClubName
            FROM InjuryRecord i
            JOIN Players p ON i.PlayerID = p.PlayerID
            LEFT JOIN Clubs c ON p.ClubID = c.ClubID
            WHERE p.PlayerName LIKE %s
            ORDER BY i.InjuryDate DESC
        """, (f"%{player_name}%",))
        
        injuries = cur.fetchall()
        if not injuries:
            print("No injuries found for this player.")
            return

        print("\nInjuries found:")
        for idx, injury in enumerate(injuries, 1):
            club = injury['ClubName'] if injury['ClubName'] else 'No Club'
            print(f"{idx}. Date: {injury['InjuryDate']}, Severity: {injury['Severity']}, Club: {club}")

        while True:
            try:
                choice = int(input("\nSelect injury number to update: ")) - 1
                if 0 <= choice < len(injuries):
                    current = injuries[choice]
                    break
                print("Invalid selection.")
            except ValueError:
                print("Please enter a valid number.")

        print("\nPress Enter to keep current values:")
        
        # Update fields
        injury_date = input(f"Enter new Injury Date (current: {current['InjuryDate']}, YYYY-MM-DD): ")
        severity = input(f"Enter new Severity (current: {current['Severity']}, Minor/Moderate/Severe/Critical): ").capitalize()
        recurrence_rate = input(f"Enter new Recurrence Rate (current: {current['RecurrenceRate']}%): ")

        # Validate and prepare updates
        update_fields = []
        params = []
        
        if injury_date:
            try:
                injury_date_obj = datetime.strptime(injury_date, '%Y-%m-%d').date()
                if injury_date_obj <= date.today():
                    update_fields.append("InjuryDate = %s")
                    params.append(injury_date)
            except ValueError:
                print("Invalid date format. Field not updated.")

        if severity:
            if severity in ["Mild", "Moderate", "Severe"]:
                update_fields.append("Severity = %s")
                params.append(severity)
            else:
                print("Invalid severity level. Field not updated.")

        if recurrence_rate:
            try:
                recurrence_rate = float(recurrence_rate)
                if 0 <= recurrence_rate <= 100:
                    update_fields.append("RecurrenceRate = %s")
                    params.append(recurrence_rate)
                else:
                    print("Invalid recurrence rate range. Field not updated.")
            except ValueError:
                print("Invalid recurrence rate format. Field not updated.")

        if update_fields:
            params.append(current['InjuryID'])
            query = f"UPDATE InjuryRecord SET {', '.join(update_fields)} WHERE InjuryID = %s"
            cur.execute(query, params)
            con.commit()
            print("Injury record updated successfully!")
        else:
            print("No valid updates provided.")

    except pymysql.Error as e:
        con.rollback()
        print(f"Database error: {e}")
    except Exception as e:
        con.rollback()
        print(f"Error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve injury records
    """
    try:
        # Option to retrieve by player or all records
        choice = input("Retrieve injuries for (A)ll players or (S)pecific player or specific (C)lub's players").upper()
        
        if choice == 'A':
            # Option to filter by severity
            filter_choice = input("Filter by severity? (Y/N): ").upper()
            
            if filter_choice == 'Y':
                print("\nStandard Severity Levels:")
                severities = ["Mild", "Moderate", "Severe"]
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
        elif choice == 'S':
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
        elif choice == 'C':
            # Take club name as input
            club_name = input("Enter Club Name to retrieve injured players: ")

            # Retrieve all injured players with related information for the specified club
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
            WHERE c.ClubName LIKE %s
            ORDER BY i.InjuryDate DESC
            """
            cur.execute(query, ('%' + club_name + '%',))
        
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