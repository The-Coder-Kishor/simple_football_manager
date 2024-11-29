# managermatchperformance.py
import pymysql

def addRecord(con, cur):
    """
    Add a new manager match performance record
    """
    try:
        # Show recent matches
        print("Recent Matches:")
        cur.execute("""
            SELECT m.MatchID, m.Date, 
                   h.ClubName as HomeTeam, m.HomeGoals,
                   a.ClubName as AwayTeam, m.AwayGoals,
                   l.LeagueName
            FROM MatchX m
            JOIN Clubs h ON m.HomeTeamID = h.ClubID
            JOIN Clubs a ON m.AwayTeamID = a.ClubID
            JOIN Leagues l ON m.LeagueID = l.LeagueID
            ORDER BY m.Date DESC
            LIMIT 10
        """)
        matches = cur.fetchall()
        
        for match in matches:
            print(f"\nMatch ID: {match['MatchID']}, Date: {match['Date']}")
            print(f"{match['HomeTeam']} {match['HomeGoals']} - {match['AwayGoals']} {match['AwayTeam']}")
            print(f"League: {match['LeagueName']}")
        
        # Get match ID
        while True:
            try:
                match_id = int(input("\nEnter Match ID: "))
                # Verify match exists
                cur.execute("SELECT MatchID FROM MatchX WHERE MatchID = %s", (match_id,))
                if cur.fetchone():
                    break
                print("Invalid Match ID.")
            except ValueError:
                print("Please enter a valid integer Match ID.")
        
        # Show managers of the teams involved
        cur.execute("""
            SELECT m.ManagerID, m.ManagerName, c.ClubName
            FROM Managers m
            JOIN Clubs c ON c.ManagerID = m.ManagerID
            WHERE c.ClubID IN (
                SELECT HomeTeamID FROM MatchX WHERE MatchID = %s
                UNION
                SELECT AwayTeamID FROM MatchX WHERE MatchID = %s
            )
        """, (match_id, match_id))
        managers = cur.fetchall()
        
        print("\nAvailable Managers:")
        for manager in managers:
            print(f"ID: {manager['ManagerID']}, Name: {manager['ManagerName']}, Club: {manager['ClubName']}")
        
        # Get manager ID
        while True:
            try:
                manager_id = int(input("\nEnter Manager ID: "))
                # Verify manager exists and is from participating teams
                if any(m['ManagerID'] == manager_id for m in managers):
                    break
                print("Invalid Manager ID or manager not from participating teams.")
            except ValueError:
                print("Please enter a valid integer Manager ID.")
        
        # Check if performance record already exists
        cur.execute("""
            SELECT * FROM ManagerMatchPerformance 
            WHERE ManagerID = %s AND MatchID = %s
        """, (manager_id, match_id))
        
        if cur.fetchone():
            print("Performance record already exists for this manager in this match.")
            return
        
        # Manager performance validation (0-10)
        while True:
            try:
                manager_performance = float(input("Enter Manager Performance Rating (0-10): "))
                if 0 <= manager_performance <= 10:
                    break
                print("Performance rating must be between 0 and 10.")
            except ValueError:
                print("Please enter a valid number for performance rating.")
        
        # Show available tactics
        print("\nAvailable Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        # Get team tactic ID
        while True:
            try:
                team_tactic_id = int(input("\nEnter Team Tactic ID: "))
                # Verify tactic exists
                cur.execute("SELECT TacticID FROM Tactics WHERE TacticID = %s", (team_tactic_id,))
                if cur.fetchone():
                    break
                print("Invalid Tactic ID.")
            except ValueError:
                print("Please enter a valid integer Tactic ID.")
        
        # Get opponent tactic ID
        while True:
            try:
                opponent_tactic_id = int(input("Enter Opponent Tactic ID: "))
                # Verify tactic exists
                cur.execute("SELECT TacticID FROM Tactics WHERE TacticID = %s", (opponent_tactic_id,))
                if cur.fetchone():
                    break
                print("Invalid Tactic ID.")
            except ValueError:
                print("Please enter a valid integer Tactic ID.")
        
        # SQL query to insert performance record
        query = """
        INSERT INTO ManagerMatchPerformance 
        (ManagerID, MatchID, ManagerPerformance, TeamTacticID, OpponentTacticID) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (manager_id, match_id, manager_performance, 
                          team_tactic_id, opponent_tactic_id))
        con.commit()
        
        print("Manager match performance record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a manager match performance record
    """
    try:
        # Show recent performance records
        print("Recent Performance Records:")
        cur.execute("""
            SELECT mmp.ManagerID, mmp.MatchID, 
                   m.ManagerName, mx.Date,
                   h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   mmp.ManagerPerformance
            FROM ManagerMatchPerformance mmp
            JOIN Managers m ON mmp.ManagerID = m.ManagerID
            JOIN MatchX mx ON mmp.MatchID = mx.MatchID
            JOIN Clubs h ON mx.HomeTeamID = h.ClubID
            JOIN Clubs a ON mx.AwayTeamID = a.ClubID
            ORDER BY mx.Date DESC
            LIMIT 20
        """)
        performances = cur.fetchall()
        
        for perf in performances:
            print(f"\nManager: {perf['ManagerName']}")
            print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']} ({perf['Date']})")
            print(f"Performance Rating: {perf['ManagerPerformance']}")
            print(f"Manager ID: {perf['ManagerID']}, Match ID: {perf['MatchID']}")
        
        # Get manager and match IDs
        while True:
            try:
                manager_id = int(input("\nEnter Manager ID: "))
                match_id = int(input("Enter Match ID: "))
                break
            except ValueError:
                print("Please enter valid integer IDs.")
        
        # SQL query to delete performance record
        query = """
        DELETE FROM ManagerMatchPerformance 
        WHERE ManagerID = %s AND MatchID = %s
        """
        
        # Execute the query
        cur.execute(query, (manager_id, match_id))
        
        if cur.rowcount > 0:
            con.commit()
            print("Performance record deleted successfully!")
        else:
            print("No matching performance record found.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a manager match performance record
    """
    try:
        # Show recent performance records
        print("Recent Performance Records:")
        cur.execute("""
            SELECT mmp.*, m.ManagerName, mx.Date,
                   h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   t1.Name as TeamTactic,
                   t2.Name as OpponentTactic
            FROM ManagerMatchPerformance mmp
            JOIN Managers m ON mmp.ManagerID = m.ManagerID
            JOIN MatchX mx ON mmp.MatchID = mx.MatchID
            JOIN Clubs h ON mx.HomeTeamID = h.ClubID
            JOIN Clubs a ON mx.AwayTeamID = a.ClubID
            JOIN Tactics t1 ON mmp.TeamTacticID = t1.TacticID
            JOIN Tactics t2 ON mmp.OpponentTacticID = t2.TacticID
            ORDER BY mx.Date DESC
            LIMIT 20
        """)
        performances = cur.fetchall()
        
        for perf in performances:
            print(f"\nManager: {perf['ManagerName']}")
            print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']} ({perf['Date']})")
            print(f"Performance Rating: {perf['ManagerPerformance']}")
            print(f"Tactics: {perf['TeamTactic']} vs {perf['OpponentTactic']}")
            print(f"Manager ID: {perf['ManagerID']}, Match ID: {perf['MatchID']}")
        
        # Get manager and match IDs
        while True:
            try:
                manager_id = int(input("\nEnter Manager ID: "))
                match_id = int(input("Enter Match ID: "))
                # Verify record exists
                cur.execute("""
                    SELECT * FROM ManagerMatchPerformance 
                    WHERE ManagerID = %s AND MatchID = %s
                """, (manager_id, match_id))
                if cur.fetchone():
                    break
                print("No performance record found for this manager and match.")
            except ValueError:
                print("Please enter valid integer IDs.")
        
        # Get updated values (allow skipping)
        print("\nPress Enter to keep current values:")
        
        # Performance rating update
        performance = input("Enter new Performance Rating (0-10): ")
        if performance:
            try:
                performance = float(performance)
                if not (0 <= performance <= 10):
                    print("Invalid performance rating. Value not updated.")
                    performance = None
            except ValueError:
                print("Invalid input. Value not updated.")
                performance = None
        
        # Show available tactics
        print("\nAvailable Tactics:")
        cur.execute("SELECT TacticID, Name, Formation FROM Tactics")
        tactics = cur.fetchall()
        for tactic in tactics:
            print(f"ID: {tactic['TacticID']}, Name: {tactic['Name']}, Formation: {tactic['Formation']}")
        
        # Team tactic update
        team_tactic_id = input("Enter new Team Tactic ID (press enter to skip): ")
        if team_tactic_id:
            try:
                team_tactic_id = int(team_tactic_id)
                cur.execute("SELECT TacticID FROM Tactics WHERE TacticID = %s", (team_tactic_id,))
                if not cur.fetchone():
                    print("Invalid tactic ID. Value not updated.")
                    team_tactic_id = None
            except ValueError:
                print("Invalid input. Value not updated.")
                team_tactic_id = None
        
        # Opponent tactic update
        opponent_tactic_id = input("Enter new Opponent Tactic ID (press enter to skip): ")
        if opponent_tactic_id:
            try:
                opponent_tactic_id = int(opponent_tactic_id)
                cur.execute("SELECT TacticID FROM Tactics WHERE TacticID = %s", (opponent_tactic_id,))
                if not cur.fetchone():
                    print("Invalid tactic ID. Value not updated.")
                    opponent_tactic_id = None
            except ValueError:
                print("Invalid input. Value not updated.")
                opponent_tactic_id = None
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if performance is not None:
            update_fields.append("ManagerPerformance = %s")
            params.append(performance)
        if team_tactic_id is not None:
            update_fields.append("TeamTacticID = %s")
            params.append(team_tactic_id)
        if opponent_tactic_id is not None:
            update_fields.append("OpponentTacticID = %s")
            params.append(opponent_tactic_id)
        
        if update_fields:
            # Add manager and match IDs to params
            params.extend([manager_id, match_id])
            
            query = f"""
            UPDATE ManagerMatchPerformance 
            SET {', '.join(update_fields)} 
            WHERE ManagerID = %s AND MatchID = %s
            """
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Performance record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating performance record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve manager match performance records
    """
    try:
        # Options for retrieval
        print("Retrieve performances by:")
        print("1. Manager")
        print("2. Match")
        print("3. Top Performances")
        print("4. Tactic Analysis")
        
        choice = input("Enter choice (1-4): ")
        
        if choice == '1':
            # Show manager performances
            manager_id = int(input("Enter Manager ID: "))
            query = """
            SELECT mmp.*, m.ManagerName,
                   mx.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName,
                   t1.Name as TeamTactic,
                   t2.Name as OpponentTactic
            FROM ManagerMatchPerformance mmp
            JOIN Managers m ON mmp.ManagerID = m.ManagerID
            JOIN MatchX mx ON mmp.MatchID = mx.MatchID
            JOIN Clubs h ON mx.HomeTeamID = h.ClubID
            JOIN Clubs a ON mx.AwayTeamID = a.ClubID
            JOIN Leagues l ON mx.LeagueID = l.LeagueID
            JOIN Tactics t1 ON mmp.TeamTacticID = t1.TacticID
            JOIN Tactics t2 ON mmp.OpponentTacticID = t2.TacticID
            WHERE mmp.ManagerID = %s
            ORDER BY mx.Date DESC
            """
            cur.execute(query, (manager_id,))
            
        elif choice == '2':
            # Show match performances
            match_id = int(input("Enter Match ID: "))
            query = """
            SELECT mmp.*, m.ManagerName,
                   mx.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName,
                   t1.Name as TeamTactic,
                   t2.Name as OpponentTactic
            FROM ManagerMatchPerformance mmp
            JOIN Managers m ON mmp.ManagerID = m.ManagerID
            JOIN MatchX mx ON mmp.MatchID = mx.MatchID
            JOIN Clubs h ON mx.HomeTeamID = h.ClubID
            JOIN Clubs a ON mx.AwayTeamID = a.ClubID
            JOIN Leagues l ON mx.LeagueID = l.LeagueID
            JOIN Tactics t1 ON mmp.TeamTacticID = t1.TacticID
            JOIN Tactics t2 ON mmp.OpponentTacticID = t2.TacticID
            WHERE mmp.MatchID = %s
            """
            cur.execute(query, (match_id,))
            
        elif choice == '3':
            # Show top performances
            query = """
            SELECT mmp.*, m.ManagerName,
                   mx.Date, h.ClubName as HomeTeam,
                   a.ClubName as AwayTeam,
                   l.LeagueName,
                   t1.Name as TeamTactic,
                   t2.Name as OpponentTactic
            FROM ManagerMatchPerformance mmp
            JOIN Managers m ON mmp.ManagerID = m.ManagerID
            JOIN MatchX mx ON mmp.MatchID = mx.MatchID
            JOIN Clubs h ON mx.HomeTeamID = h.ClubID
            JOIN Clubs a ON mx.AwayTeamID = a.ClubID
            JOIN Leagues l ON mx.LeagueID = l.LeagueID
            JOIN Tactics t1 ON mmp.TeamTacticID = t1.TacticID
            JOIN Tactics t2 ON mmp.OpponentTacticID = t2.TacticID
            ORDER BY mmp.ManagerPerformance DESC
            LIMIT 10
            """
            cur.execute(query)
            
        elif choice == '4':
            # Tactic analysis
            query = """
            SELECT t1.Name as TeamTactic,
                   t2.Name as OpponentTactic,
                   AVG(mmp.ManagerPerformance) as AvgPerformance,
                   COUNT(*) as TimesUsed
            FROM ManagerMatchPerformance mmp
            JOIN Tactics t1 ON mmp.TeamTacticID = t1.TacticID
            JOIN Tactics t2 ON mmp.OpponentTacticID = t2.TacticID
            GROUP BY t1.Name, t2.Name
            ORDER BY AvgPerformance DESC
            """
            cur.execute(query)
            
            # Fetch and display tactic analysis
            results = cur.fetchall()
            if results:
                print("\nTactic Analysis:")
                for result in results:
                    print(f"\nTeam Tactic: {result['TeamTactic']}")
                    print(f"vs Opponent Tactic: {result['OpponentTactic']}")
                    print(f"Average Performance: {result['AvgPerformance']:.2f}")
                    print(f"Times Used: {result['TimesUsed']}")
            return
        
        # Fetch and display results for other choices
        results = cur.fetchall()
        
        if not results:
            print("No performance records found.")
        else:
            for perf in results:
                print("\nPerformance Details:")
                print(f"Manager: {perf['ManagerName']}")
                print(f"Match: {perf['HomeTeam']} vs {perf['AwayTeam']}")
                print(f"Date: {perf['Date']}")
                print(f"League: {perf['LeagueName']}")
                print(f"Performance Rating: {perf['ManagerPerformance']}")
                print(f"Team Tactic: {perf['TeamTactic']}")
                print(f"Opponent Tactic: {perf['OpponentTactic']}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving performance records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")