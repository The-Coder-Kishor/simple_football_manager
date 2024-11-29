# playsin.py
import pymysql

def addRecord(con, cur):
    """
    Add a new plays-in record after searching for club and league
    """
    try:
        # Get search criteria
        club_name = input("Enter club name to search: ")
        league_name = input("Enter league name to search: ")
        year_input = input("Enter year: ")

        # Search for matching clubs
        cur.execute("""
            SELECT ClubID, ClubName
            FROM Clubs
            WHERE ClubName LIKE %s
        """, (f"%{club_name}%",))
        clubs = cur.fetchall()

        if not clubs:
            print("No matching clubs found.")
            return

        print("\nMatching Clubs:")
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")

        # Search for matching leagues
        cur.execute("""
            SELECT LeagueID, LeagueName, LeagueYear
            FROM Leagues
            WHERE LeagueName LIKE %s
            AND (%s = '' OR LeagueYear = %s)
        """, (f"%{league_name}%", year_input, year_input))
        leagues = cur.fetchall()

        if not leagues:
            print("No matching leagues found.")
            return

        print("\nMatching Leagues:")
        for league in leagues:
            print(f"ID: {league['LeagueID']}, Name: {league['LeagueName']}, "
                  f"Year: {league['LeagueYear']}")

        # Get IDs for the record to add
        while True:
            try:
                club_id = int(input("\nEnter Club ID from above: "))
                league_id = int(input("Enter League ID from above: "))
                points = int(input("Enter Points: "))
                break
            except ValueError:
                print("Please enter valid integer values.")

        # Continue with the existing add logic...
        # [Rest of the add record logic]

    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a plays-in record after searching for club and league
    """
    try:
        # Get search criteria
        club_name = input("Enter club name to search: ")
        league_name = input("Enter league name to search: ")
        year_input = input("Enter year: ")

        # Search for matching records
        query = """
        SELECT c.ClubID, c.ClubName,
               l.LeagueID, l.LeagueName, l.LeagueYear,
               p.Points
        FROM PlaysIn p
        JOIN Clubs c ON p.ClubID = c.ClubID
        JOIN Leagues l ON p.LeagueID = l.LeagueID
        WHERE c.ClubName LIKE %s
        AND l.LeagueName LIKE %s
        """
        params = [f"%{club_name}%", f"%{league_name}%"]

        if year_input:
            try:
                year = int(year_input)
                query += " AND l.LeagueYear = %s"
                params.append(year)
            except ValueError:
                print("Invalid year format. Showing results for all years.")

        cur.execute(query, params)
        records = cur.fetchall()

        if not records:
            print("No matching records found.")
            return

        # Display matching records
        print("\nMatching Records:")
        for record in records:
            print(f"\nClub: {record['ClubName']} (ID: {record['ClubID']})")
            print(f"League: {record['LeagueName']} (ID: {record['LeagueID']})")
            print(f"Year: {record['LeagueYear']}")
            print(f"Points: {record['Points']}")

        # Get IDs for the record to delete
        while True:
            try:
                club_id = int(input("\nEnter Club ID from above to delete: "))
                league_id = int(input("Enter League ID from above to delete: "))
                
                # Verify the selected combination exists
                cur.execute("""
                    SELECT * FROM PlaysIn 
                    WHERE ClubID = %s AND LeagueID = %s
                """, (club_id, league_id))
                
                if not cur.fetchone():
                    print("No matching record found for the selected IDs.")
                    continue
                break
            except ValueError:
                print("Please enter valid integer IDs.")

        # Confirm deletion
        confirm = input("\nAre you sure you want to delete this record? (y/n): ").lower()
        if confirm != 'y':
            print("Deletion cancelled.")
            return

        # Delete the record
        cur.execute("""
            DELETE FROM PlaysIn 
            WHERE ClubID = %s AND LeagueID = %s
        """, (club_id, league_id))
        
        con.commit()
        print("Record deleted successfully!")

    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a plays-in record after searching for club and league
    """
    try:
        # Get search criteria
        club_name = input("Enter club name to search: ")
        league_name = input("Enter league name to search: ")
        year_input = input("Enter year: ")

        # Search for matching records
        query = """
        SELECT c.ClubID, c.ClubName,
               l.LeagueID, l.LeagueName, l.LeagueYear,
               p.Points
        FROM PlaysIn p
        JOIN Clubs c ON p.ClubID = c.ClubID
        JOIN Leagues l ON p.LeagueID = l.LeagueID
        WHERE c.ClubName LIKE %s
        AND l.LeagueName LIKE %s
        """
        params = [f"%{club_name}%", f"%{league_name}%"]

        if year_input:
            try:
                year = int(year_input)
                query += " AND l.LeagueYear = %s"
                params.append(year)
            except ValueError:
                print("Invalid year format. Showing results for all years.")

        cur.execute(query, params)
        records = cur.fetchall()

        if not records:
            print("No matching records found.")
            return

        # Display matching records
        print("\nMatching Records:")
        for record in records:
            print(f"\nClub: {record['ClubName']} (ID: {record['ClubID']})")
            print(f"League: {record['LeagueName']} (ID: {record['LeagueID']})")
            print(f"Year: {record['LeagueYear']}")
            print(f"Current Points: {record['Points']}")

        # Get IDs for the record to update
        while True:
            try:
                club_id = int(input("\nEnter Club ID from above to update: "))
                league_id = int(input("Enter League ID from above to update: "))
                
                # Verify the selected combination exists
                cur.execute("""
                    SELECT * FROM PlaysIn 
                    WHERE ClubID = %s AND LeagueID = %s
                """, (club_id, league_id))
                
                if not cur.fetchone():
                    print("No matching record found for the selected IDs.")
                    continue
                break
            except ValueError:
                print("Please enter valid integer IDs.")

        # Get new points value
        while True:
            try:
                new_points = int(input("Enter new points value: "))
                if new_points < 0:
                    print("Points cannot be negative.")
                    continue
                break
            except ValueError:
                print("Please enter a valid integer for points.")

        # Update the record
        cur.execute("""
            UPDATE PlaysIn 
            SET Points = %s 
            WHERE ClubID = %s AND LeagueID = %s
        """, (new_points, club_id, league_id))
        
        con.commit()
        print("Record updated successfully!")

    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve plays-in records with three options:
    1. All records
    2. Records by Club
    3. Records by League Name and Year
    """
    try:
        print("\nRetrieval Options:")
        print("1. (A)ll records")
        print("2. Records by (C)lub")
        print("3. Records by (L)eague name and year")
        choice = input("\nEnter your choice (A/C/L): ").upper()

        if choice == 'A':
            # Retrieve all records
            query = """
            SELECT c.ClubName,
                   l.LeagueName, l.LeagueYear,
                   p.Points
            FROM PlaysIn p
            JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Leagues l ON p.LeagueID = l.LeagueID
            ORDER BY l.LeagueYear DESC, l.LeagueName, c.ClubName
            """
            cur.execute(query)
            results = cur.fetchall()

            if not results:
                print("No records found.")
                return

            print("\nAll League Participation Records:")
            print("\n{:<30} {:<30} {:<10} {:<10}".format(
                "Club Name", "League Name", "Year", "Points"))
            print("-" * 80)
            
            for result in results:
                print("{:<30} {:<30} {:<10} {:<10}".format(
                    result['ClubName'],
                    result['LeagueName'],
                    str(result['LeagueYear']),
                    str(result['Points'])
                ))

        elif choice == 'C':
            # Get club name from user
            club_name = input("Enter club name (or part of name): ")

            query = """
            SELECT c.ClubName,
                   l.LeagueName, l.LeagueYear,
                   p.Points
            FROM PlaysIn p
            JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Leagues l ON p.LeagueID = l.LeagueID
            WHERE c.ClubName LIKE %s
            ORDER BY l.LeagueYear DESC, l.LeagueName
            """
            cur.execute(query, (f"%{club_name}%",))
            results = cur.fetchall()

            if not results:
                print(f"No records found for clubs matching '{club_name}'")
                return

            print(f"\nRecords for clubs matching '{club_name}':")
            print("\n{:<30} {:<30} {:<10} {:<10}".format(
                "Club Name", "League Name", "Year", "Points"))
            print("-" * 80)
            
            for result in results:
                print("{:<30} {:<30} {:<10} {:<10}".format(
                    result['ClubName'],
                    result['LeagueName'],
                    str(result['LeagueYear']),
                    str(result['Points'])
                ))

        elif choice == 'L':
            # Get league name and year
            league_name = input("Enter league name (or part of name): ")
            while True:
                try:
                    league_year = int(input("Enter league year: "))
                    break
                except ValueError:
                    print("Please enter a valid year (e.g., 2023)")

            query = """
            SELECT c.ClubName,
                   l.LeagueName, l.LeagueYear,
                   p.Points
            FROM PlaysIn p
            JOIN Clubs c ON p.ClubID = c.ClubID
            JOIN Leagues l ON p.LeagueID = l.LeagueID
            WHERE l.LeagueName LIKE %s
            AND l.LeagueYear = %s
            ORDER BY p.Points DESC, c.ClubName
            """
            cur.execute(query, (f"%{league_name}%", league_year))
            results = cur.fetchall()

            if not results:
                print(f"No records found for league '{league_name}' in year {league_year}")
                return

            print(f"\nStandings for {results[0]['LeagueName']} ({league_year}):")
            print("\n{:<5} {:<30} {:<10}".format(
                "Pos", "Club Name", "Points"))
            print("-" * 45)
            
            for pos, result in enumerate(results, 1):
                print("{:<5} {:<30} {:<10}".format(
                    pos,
                    result['ClubName'],
                    str(result['Points'])
                ))

        else:
            print("Invalid choice. Please enter 'A' for all records, 'C' for club search, or 'L' for league search.")

    except pymysql.Error as e:
        print(f"Error retrieving records: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")