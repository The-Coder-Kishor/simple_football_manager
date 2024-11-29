import pymysql

def addRecord(con, cur):
    """
    Add a new league record
    """
    try:
        # First check if the league name exists in LeagueDetails
        league_name = input("Enter League Name (must exist in LeagueDetails): ")
        cur.execute("SELECT LeagueName FROM LeagueDetails WHERE LeagueName = %s", (league_name,))
        if not cur.fetchone():
            print("Error: League name must exist in LeagueDetails table first.")
            return

        # League year validation
        while True:
            try:
                league_year = int(input("Enter League Year (YYYY): "))
                if 1800 <= league_year <= 9999:
                    break
                print("Year must be between 1800 and 9999.")
            except ValueError:
                print("Please enter a valid year.")

        # Show available clubs for winning club selection
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")

        # Get winning club ID (optional)
        winning_club_id = input("Enter Winning Club ID (press enter to skip): ")
        winning_club_id = int(winning_club_id) if winning_club_id else None

        # Show available players for top scorer/assist/clean sheet selection
        print("\nAvailable Players:")
        cur.execute("SELECT PlayerID, PlayerName FROM Players")
        players = cur.fetchall()
        for player in players:
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")

        # Get top performer IDs (optional)
        top_scorer_id = input("Enter Top Scorer Player ID (press enter to skip): ")
        top_scorer_id = int(top_scorer_id) if top_scorer_id else None

        top_assist_id = input("Enter Top Assist Player ID (press enter to skip): ")
        top_assist_id = int(top_assist_id) if top_assist_id else None

        top_clean_sheet_id = input("Enter Top Clean Sheet Player ID (press enter to skip): ")
        top_clean_sheet_id = int(top_clean_sheet_id) if top_clean_sheet_id else None

        # Check if league with same name and year already exists
        cur.execute("SELECT LeagueID FROM Leagues WHERE LeagueName = %s AND LeagueYear = %s", 
                    (league_name, league_year))
        if cur.fetchone():
            print(f"Error: A league for {league_name} in {league_year} already exists.")
            return

        # SQL query to insert league
        query = """
        INSERT INTO Leagues 
        (LeagueName, LeagueYear, WinningClubID, 
         TopScorerID, TopAssistID, TopCleanSheetID) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # Execute the query
        cur.execute(query, (league_name, league_year, winning_club_id, 
                            top_scorer_id, top_assist_id, top_clean_sheet_id))
        con.commit()

        print("League record added successfully!")
        print(f"New League: {league_name} {league_year}")

    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding league record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a league record
    """
    try:
        # Get league details to delete
        league_name = input("Enter League Name to delete: ")
        league_year = int(input("Enter League Year to delete: "))

        # SQL query to delete league
        query = "DELETE FROM Leagues WHERE LeagueName = %s AND LeagueYear = %s"

        # Execute the query
        cur.execute(query, (league_name, league_year))

        if cur.rowcount > 0:
            con.commit()
            print(f"League {league_name} for year {league_year} deleted successfully!")
        else:
            print(f"No league found with name {league_name} for year {league_year}")

    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting league record: {e}")
    except ValueError:
        print("Please enter a valid year.")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a league record
    """
    try:
        # Get current league details
        league_name = input("Enter League Name to update: ")
        league_year = int(input("Enter League Year to update: "))

        # Verify league exists
        cur.execute("SELECT * FROM Leagues WHERE LeagueName = %s AND LeagueYear = %s", 
                    (league_name, league_year))
        if not cur.fetchone():
            print(f"No league found with name {league_name} for year {league_year}")
            return

        # Show available clubs for winning club selection
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")

        # Get winning club ID (optional)
        winning_club_id = input("Enter new Winning Club ID (press enter to skip, 'null' to remove): ")
        
        # Show available players for top scorer/assist/clean sheet selection
        print("\nAvailable Players:")
        cur.execute("SELECT PlayerID, PlayerName FROM Players")
        players = cur.fetchall()
        for player in players:
            print(f"ID: {player['PlayerID']}, Name: {player['PlayerName']}")

        # Get top performer IDs (optional)
        top_scorer_id = input("Enter new Top Scorer ID (press enter to skip, 'null' to remove): ")
        top_assist_id = input("Enter new Top Assist ID (press enter to skip, 'null' to remove): ")
        top_clean_sheet_id = input("Enter new Top Clean Sheet ID (press enter to skip, 'null' to remove): ")

        # Prepare update query dynamically
        update_fields = []
        params = []

        # Handle optional IDs
        if winning_club_id:
            if winning_club_id.lower() == 'null':
                update_fields.append("WinningClubID = NULL")
            else:
                update_fields.append("WinningClubID = %s")
                params.append(int(winning_club_id))
        if top_scorer_id:
            if top_scorer_id.lower() == 'null':
                update_fields.append("TopScorerID = NULL")
            else:
                update_fields.append("TopScorerID = %s")
                params.append(int(top_scorer_id))
        if top_assist_id:
            if top_assist_id.lower() == 'null':
                update_fields.append("TopAssistID = NULL")
            else:
                update_fields.append("TopAssistID = %s")
                params.append(int(top_assist_id))
        if top_clean_sheet_id:
            if top_clean_sheet_id.lower() == 'null':
                update_fields.append("TopCleanSheetID = NULL")
            else:
                update_fields.append("TopCleanSheetID = %s")
                params.append(int(top_clean_sheet_id))

        # Add league name and year to params
        params.extend([league_name, league_year])

        if update_fields:
            query = f"UPDATE Leagues SET {', '.join(update_fields)} WHERE LeagueName = %s AND LeagueYear = %s"

            # Execute the query
            cur.execute(query, params)
            con.commit()

            print("League record updated successfully!")
        else:
            print("No updates specified.")

    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating league record: {e}")
    except ValueError:
        print("Please enter a valid ID.")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve league records
    """
    try:
        # Retrieve specific league
        league_name = input("Enter League Name: ")
        league_year = int(input("Enter League Year: "))

        query = """
        SELECT l.*,
               c.ClubName as WinningClubName,
               ts.PlayerName as TopScorerName,
               ta.PlayerName as TopAssistName,
               tc.PlayerName as TopCleanSheetName,
               ld.Nation,
               ld.NoOfTeams,
               ld.PromotionLevel,
               ld.RelegationLevel
        FROM Leagues l
        LEFT JOIN Clubs c ON l.WinningClubID = c.ClubID
        LEFT JOIN Players ts ON l.TopScorerID = ts.PlayerID
        LEFT JOIN Players ta ON l.TopAssistID = ta.PlayerID
        LEFT JOIN Players tc ON l.TopCleanSheetID = tc.PlayerID
        LEFT JOIN LeagueDetails ld ON l.LeagueName = ld.LeagueName
        WHERE l.LeagueName = %s AND l.LeagueYear = %s
        """
        cur.execute(query, (league_name, league_year))

        # Fetch and display results
        results = cur.fetchall()

        if not results:
            print(f"No league found with name {league_name} for year {league_year}")
        else:
            for league in results:
                print("\nLeague Details:")
                print(f"League ID: {league['LeagueID']}")
                print(f"Name: {league['LeagueName']}")
                print(f"Year: {league['LeagueYear']}")
                print(f"Nation: {league['Nation']}")
                print(f"Number of Teams: {league['NoOfTeams']}")
                print(f"Promotion Level: {league['PromotionLevel']}")
                print(f"Relegation Level: {league['RelegationLevel']}")
                print(f"Winning Club: {league['WinningClubName'] if league['WinningClubName'] else 'Not Set'}")
                print(f"Top Scorer: {league['TopScorerName'] if league['TopScorerName'] else 'Not Set'}")
                print(f"Top Assist: {league['TopAssistName'] if league['TopAssistName'] else 'Not Set'}")
                print(f"Top Clean Sheet: {league['TopCleanSheetName'] if league['TopCleanSheetName'] else 'Not Set'}")

    except pymysql.Error as e:
        print(f"Error retrieving league records: {e}")
    except ValueError:
        print("Please enter a valid year.")
    except Exception as e:
        print(f"Unexpected error: {e}")