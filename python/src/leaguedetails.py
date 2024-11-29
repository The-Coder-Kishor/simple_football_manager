# leaguedetails.py
import pymysql

def addRecord(con, cur):
    """
    Add a new league details record
    """
    try:
        # Collect league details
        league_name = input("Enter League Name: ")
        nation = input("Enter Nation: ")
        
        # Number of teams validation
        while True:
            try:
                no_of_teams = int(input("Enter Number of Teams: "))
                if no_of_teams > 0:
                    break
                print("Number of teams must be greater than 0.")
            except ValueError:
                print("Please enter a valid integer for number of teams.")
        
        # Promotion level validation
        while True:
            try:
                promotion_level = int(input("Enter Promotion Level (0-5): "))
                if 0 <= promotion_level <= 5:
                    break
                print("Promotion level must be between 0 and 5.")
            except ValueError:
                print("Please enter a valid integer for promotion level.")
        
        # Relegation level validation
        while True:
            try:
                relegation_level = int(input("Enter Relegation Level (0-5): "))
                if 0 <= relegation_level <= 5:
                    break
                print("Relegation level must be between 0 and 5.")
            except ValueError:
                print("Please enter a valid integer for relegation level.")
        
        # SQL query to insert league details
        query = """
        INSERT INTO LeagueDetails 
        (LeagueName, Nation, NoOfTeams, PromotionLevel, RelegationLevel) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (league_name, nation, no_of_teams, promotion_level, relegation_level))
        con.commit()
        
        print("League details record added successfully!")
        print(f"New League Details: {league_name} ({nation})")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding league details record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a league details record
    """
    try:
        # Retrieve and display league details to help user choose
        print("Current League Details:")
        cur.execute("SELECT LeagueName, Nation, NoOfTeams FROM LeagueDetails")
        leagues = cur.fetchall()
        
        for league in leagues:
            print(f"Name: {league['LeagueName']}, Nation: {league['Nation']}, Teams: {league['NoOfTeams']}")
        
        # Get league name to delete
        league_name = input("Enter League Name to delete: ")
        
        # Check if league name is referenced in Leagues table
        cur.execute("SELECT COUNT(*) as count FROM Leagues WHERE LeagueName = %s", (league_name,))
        if cur.fetchone()['count'] > 0:
            print("Cannot delete: This league is referenced in the Leagues table.")
            return
        
        # SQL query to delete league details
        query = "DELETE FROM LeagueDetails WHERE LeagueName = %s"
        
        # Execute the query
        cur.execute(query, (league_name,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"League details for {league_name} deleted successfully!")
        else:
            print(f"No league details found with name {league_name}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting league details record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a league details record
    """
    try:
        # Retrieve and display league details to help user choose
        print("Current League Details:")
        cur.execute("SELECT LeagueName, Nation, NoOfTeams FROM LeagueDetails")
        leagues = cur.fetchall()
        
        for league in leagues:
            print(f"Name: {league['LeagueName']}, Nation: {league['Nation']}, Teams: {league['NoOfTeams']}")
        
        # Get league name to update
        league_name = input("Enter League Name to update: ")
        
        # Check if league exists
        cur.execute("SELECT * FROM LeagueDetails WHERE LeagueName = %s", (league_name,))
        if not cur.fetchone():
            print(f"No league details found with name {league_name}")
            return
        
        # Collect new details (allow skipping)
        new_league_name = input("Enter new League Name (press enter to skip): ")
        nation = input("Enter new Nation (press enter to skip): ")
        
        no_of_teams = input("Enter new Number of Teams (press enter to skip): ")
        if no_of_teams:
            while True:
                try:
                    no_of_teams = int(no_of_teams)
                    if no_of_teams > 0:
                        break
                    no_of_teams = input("Number of teams must be greater than 0: ")
                except ValueError:
                    no_of_teams = input("Please enter a valid integer for number of teams: ")
        
        promotion_level = input("Enter new Promotion Level (0-5) (press enter to skip): ")
        if promotion_level:
            while True:
                try:
                    promotion_level = int(promotion_level)
                    if 0 <= promotion_level <= 5:
                        break
                    promotion_level = input("Promotion level must be between 0 and 5: ")
                except ValueError:
                    promotion_level = input("Please enter a valid integer for promotion level: ")
        
        relegation_level = input("Enter new Relegation Level (0-5) (press enter to skip): ")
        if relegation_level:
            while True:
                try:
                    relegation_level = int(relegation_level)
                    if 0 <= relegation_level <= 5:
                        break
                    relegation_level = input("Relegation level must be between 0 and 5: ")
                except ValueError:
                    relegation_level = input("Please enter a valid integer for relegation level: ")
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if new_league_name:
            update_fields.append("LeagueName = %s")
            params.append(new_league_name)
        if nation:
            update_fields.append("Nation = %s")
            params.append(nation)
        if no_of_teams:
            update_fields.append("NoOfTeams = %s")
            params.append(no_of_teams)
        if promotion_level:
            update_fields.append("PromotionLevel = %s")
            params.append(promotion_level)
        if relegation_level:
            update_fields.append("RelegationLevel = %s")
            params.append(relegation_level)
        
        # Add current league name to params
        params.append(league_name)
        
        if update_fields:
            query = f"UPDATE LeagueDetails SET {', '.join(update_fields)} WHERE LeagueName = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("League details updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating league details record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve league details records
    """
    try:
        # Option to retrieve all or specific league details
        choice = input("Retrieve (A)ll or (S)pecific league details? ").upper()
        
        if choice == 'A':
            # Retrieve all league details
            query = """
            SELECT ld.*, 
                   COUNT(l.LeagueID) as ActiveSeasons
            FROM LeagueDetails ld
            LEFT JOIN Leagues l ON ld.LeagueName = l.LeagueName
            GROUP BY ld.LeagueName
            """
            cur.execute(query)
        else:
            # Retrieve specific league details
            league_name = input("Enter League Name: ")
            query = """
            SELECT ld.*, 
                   COUNT(l.LeagueID) as ActiveSeasons
            FROM LeagueDetails ld
            LEFT JOIN Leagues l ON ld.LeagueName = l.LeagueName
            WHERE ld.LeagueName = %s
            GROUP BY ld.LeagueName
            """
            cur.execute(query, (league_name,))
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No league details found.")
        else:
            for league in results:
                print("\nLeague Details:")
                print(f"League Name: {league['LeagueName']}")
                print(f"Nation: {league['Nation']}")
                print(f"Number of Teams: {league['NoOfTeams']}")
                print(f"Promotion Level: {league['PromotionLevel']}")
                print(f"Relegation Level: {league['RelegationLevel']}")
                print(f"Active Seasons: {league['ActiveSeasons']}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving league details records: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")