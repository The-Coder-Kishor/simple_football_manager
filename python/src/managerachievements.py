# managerachievements.py
import pymysql
from datetime import datetime, date

def addRecord(con, cur):
    """
    Add a new manager achievement record
    """
    try:
        # Show managers
        print("Available Managers:")
        cur.execute("""
            SELECT m.ManagerID, m.ManagerName, c.ClubName, 
                   COUNT(ma.AchievementID) as TotalAchievements
            FROM Managers m
            LEFT JOIN Clubs c ON m.ManagerID = c.ManagerID
            LEFT JOIN ManagerAchievements ma ON m.ManagerID = ma.ManagerID
            GROUP BY m.ManagerID, m.ManagerName, c.ClubName
            ORDER BY m.ManagerName
        """)
        managers = cur.fetchall()
        
        for manager in managers:
            club = manager['ClubName'] if manager['ClubName'] else 'No Club'
            print(f"\nID: {manager['ManagerID']}, Name: {manager['ManagerName']}")
            print(f"Current Club: {club}")
            print(f"Total Achievements: {manager['TotalAchievements']}")
        
        # Get manager ID
        while True:
            try:
                manager_id = int(input("\nEnter Manager ID: "))
                # Verify manager exists
                cur.execute("SELECT ManagerID FROM Managers WHERE ManagerID = %s", (manager_id,))
                if cur.fetchone():
                    break
                print("Invalid Manager ID.")
            except ValueError:
                print("Please enter a valid integer Manager ID.")
        
        # Get achievement description
        achievement_desc = input("Enter Achievement Description: ").strip()
        while not achievement_desc:
            print("Achievement description cannot be empty.")
            achievement_desc = input("Enter Achievement Description: ").strip()
        
        # Achievement date validation
        while True:
            achievement_date = input("Enter Achievement Date (YYYY-MM-DD): ")
            try:
                achievement_date_obj = datetime.strptime(achievement_date, '%Y-%m-%d').date()
                if achievement_date_obj > date.today():
                    print("Achievement date cannot be in the future.")
                    continue
                break
            except ValueError:
                print("Please enter a valid date in YYYY-MM-DD format.")
        
        # Show available clubs
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs ORDER BY ClubName")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
        
        # Get club ID (optional)
        club_id = input("\nEnter Club ID (press enter to skip): ")
        club_id = int(club_id) if club_id else None
        
        # Show available leagues
        print("\nAvailable Leagues:")
        cur.execute("SELECT LeagueID, LeagueName, LeagueYear FROM Leagues ORDER BY LeagueYear DESC, LeagueName")
        leagues = cur.fetchall()
        for league in leagues:
            print(f"ID: {league['LeagueID']}, {league['LeagueName']} ({league['LeagueYear']})")
        
        # Get league ID (optional)
        league_id = input("\nEnter League ID (press enter to skip): ")
        league_id = int(league_id) if league_id else None
        
        # SQL query to insert achievement
        query = """
        INSERT INTO ManagerAchievements 
        (ManagerID, AchievementDescription, Date, ClubID, LeagueID) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        # Execute the query
        cur.execute(query, (manager_id, achievement_desc, achievement_date, club_id, league_id))
        con.commit()
        
        print("Manager achievement record added successfully!")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error adding achievement record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def deleteRecord(con, cur):
    """
    Delete a manager achievement record
    """
    try:
        # Show achievements
        print("Manager Achievements:")
        cur.execute("""
            SELECT ma.AchievementID, m.ManagerName, 
                   ma.AchievementDescription, ma.Date,
                   c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            ORDER BY ma.Date DESC
        """)
        achievements = cur.fetchall()
        
        for achievement in achievements:
            print(f"\nID: {achievement['AchievementID']}")
            print(f"Manager: {achievement['ManagerName']}")
            print(f"Achievement: {achievement['AchievementDescription']}")
            print(f"Date: {achievement['Date']}")
            if achievement['ClubName']:
                print(f"Club: {achievement['ClubName']}")
            if achievement['LeagueName']:
                print(f"League: {achievement['LeagueName']}")
        
        # Get achievement ID to delete
        while True:
            try:
                achievement_id = int(input("\nEnter Achievement ID to delete: "))
                break
            except ValueError:
                print("Please enter a valid integer Achievement ID.")
        
        # SQL query to delete achievement
        query = "DELETE FROM ManagerAchievements WHERE AchievementID = %s"
        
        # Execute the query
        cur.execute(query, (achievement_id,))
        
        if cur.rowcount > 0:
            con.commit()
            print(f"Achievement with ID {achievement_id} deleted successfully!")
        else:
            print(f"No achievement found with ID {achievement_id}")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error deleting achievement record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def updateRecord(con, cur):
    """
    Update a manager achievement record
    """
    try:
        # Show achievements
        print("Manager Achievements:")
        cur.execute("""
            SELECT ma.AchievementID, m.ManagerName, 
                   ma.AchievementDescription, ma.Date,
                   c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            ORDER BY ma.Date DESC
        """)
        achievements = cur.fetchall()
        
        for achievement in achievements:
            print(f"\nID: {achievement['AchievementID']}")
            print(f"Manager: {achievement['ManagerName']}")
            print(f"Achievement: {achievement['AchievementDescription']}")
            print(f"Date: {achievement['Date']}")
            if achievement['ClubName']:
                print(f"Club: {achievement['ClubName']}")
            if achievement['LeagueName']:
                print(f"League: {achievement['LeagueName']}")
        
        # Get achievement ID to update
        while True:
            try:
                achievement_id = int(input("\nEnter Achievement ID to update: "))
                # Verify achievement exists
                cur.execute("SELECT * FROM ManagerAchievements WHERE AchievementID = %s", (achievement_id,))
                if cur.fetchone():
                    break
                print("No achievement found with this ID.")
            except ValueError:
                print("Please enter a valid integer Achievement ID.")
        
        # Get updated values (allow skipping)
        print("\nPress Enter to keep current values:")
        
        # Achievement description update
        achievement_desc = input("Enter new Achievement Description: ").strip()
        
        # Achievement date update
        achievement_date = input("Enter new Achievement Date (YYYY-MM-DD): ")
        if achievement_date:
            try:
                achievement_date_obj = datetime.strptime(achievement_date, '%Y-%m-%d').date()
                if achievement_date_obj > date.today():
                    print("Achievement date cannot be in the future. Value not updated.")
                    achievement_date = None
            except ValueError:
                print("Invalid date format. Value not updated.")
                achievement_date = None
        
        # Show available clubs
        print("\nAvailable Clubs:")
        cur.execute("SELECT ClubID, ClubName FROM Clubs ORDER BY ClubName")
        clubs = cur.fetchall()
        for club in clubs:
            print(f"ID: {club['ClubID']}, Name: {club['ClubName']}")
        
        # Club ID update
        club_id = input("\nEnter new Club ID (press enter to skip, 'null' to remove): ")
        if club_id:
            if club_id.lower() == 'null':
                club_id = None
            else:
                try:
                    club_id = int(club_id)
                    cur.execute("SELECT ClubID FROM Clubs WHERE ClubID = %s", (club_id,))
                    if not cur.fetchone():
                        print("Invalid Club ID. Value not updated.")
                        club_id = 'skip'
                except ValueError:
                    print("Invalid input. Value not updated.")
                    club_id = 'skip'
        
        # Show available leagues
        print("\nAvailable Leagues:")
        cur.execute("SELECT LeagueID, LeagueName, LeagueYear FROM Leagues ORDER BY LeagueYear DESC, LeagueName")
        leagues = cur.fetchall()
        for league in leagues:
            print(f"ID: {league['LeagueID']}, {league['LeagueName']} ({league['LeagueYear']})")
        
        # League ID update
        league_id = input("\nEnter new League ID (press enter to skip, 'null' to remove): ")
        if league_id:
            if league_id.lower() == 'null':
                league_id = None
            else:
                try:
                    league_id = int(league_id)
                    cur.execute("SELECT LeagueID FROM Leagues WHERE LeagueID = %s", (league_id,))
                    if not cur.fetchone():
                        print("Invalid League ID. Value not updated.")
                        league_id = 'skip'
                except ValueError:
                    print("Invalid input. Value not updated.")
                    league_id = 'skip'
        
        # Prepare update query dynamically
        update_fields = []
        params = []
        
        if achievement_desc:
            update_fields.append("AchievementDescription = %s")
            params.append(achievement_desc)
        if achievement_date:
            update_fields.append("Date = %s")
            params.append(achievement_date)
        if club_id != 'skip':
            update_fields.append("ClubID = %s")
            params.append(club_id)
        if league_id != 'skip':
            update_fields.append("LeagueID = %s")
            params.append(league_id)
        
        if update_fields:
            # Add achievement ID to params
            params.append(achievement_id)
            
            query = f"UPDATE ManagerAchievements SET {', '.join(update_fields)} WHERE AchievementID = %s"
            
            # Execute the query
            cur.execute(query, params)
            con.commit()
            
            print("Achievement record updated successfully!")
        else:
            print("No updates specified.")
    
    except pymysql.Error as e:
        con.rollback()
        print(f"Error updating achievement record: {e}")
    except Exception as e:
        con.rollback()
        print(f"Unexpected error: {e}")

def retrieveRecord(con, cur):
    """
    Retrieve manager achievement records
    """
    try:
        # Options for retrieval
        print("Retrieve achievements by:")
        print("1. Manager")
        print("2. Club")
        print("3. League")
        print("4. Year")
        
        choice = input("Enter choice (1-4): ")
        
        if choice == '1':
            # Show managers
            manager_id = int(input("Enter Manager ID: "))
            query = """
            SELECT ma.*, m.ManagerName, c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            WHERE ma.ManagerID = %s
            ORDER BY ma.Date DESC
            """
            cur.execute(query, (manager_id,))
            
        elif choice == '2':
            # Show club achievements
            club_id = int(input("Enter Club ID: "))
            query = """
            SELECT ma.*, m.ManagerName, c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            WHERE ma.ClubID = %s
            ORDER BY ma.Date DESC
            """
            cur.execute(query, (club_id,))
            
        elif choice == '3':
            # Show league achievements
            league_id = int(input("Enter League ID: "))
            query = """
            SELECT ma.*, m.ManagerName, c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            WHERE ma.LeagueID = %s
            ORDER BY ma.Date DESC
            """
            cur.execute(query, (league_id,))
            
        elif choice == '4':
            # Show achievements by year
            year = input("Enter Year (YYYY): ")
            query = """
            SELECT ma.*, m.ManagerName, c.ClubName, l.LeagueName
            FROM ManagerAchievements ma
            JOIN Managers m ON ma.ManagerID = m.ManagerID
            LEFT JOIN Clubs c ON ma.ClubID = c.ClubID
            LEFT JOIN Leagues l ON ma.LeagueID = l.LeagueID
            WHERE YEAR(ma.Date) = %s
            ORDER BY ma.Date DESC
            """
            cur.execute(query, (year,))
        
        else:
            print("Invalid choice.")
            return
        
        # Fetch and display results
        results = cur.fetchall()
        
        if not results:
            print("No achievements found.")
        else:
            current_year = None
            for achievement in results:
                year = achievement['Date'].year
                if year != current_year:
                    current_year = year
                    print(f"\n=== {year} ===")
                
                print(f"\nAchievement ID: {achievement['AchievementID']}")
                print(f"Manager: {achievement['ManagerName']}")
                print(f"Achievement: {achievement['AchievementDescription']}")
                print(f"Date: {achievement['Date']}")
                if achievement['ClubName']:
                    print(f"Club: {achievement['ClubName']}")
                if achievement['LeagueName']:
                    print(f"League: {achievement['LeagueName']}")
                print("---")
    
    except pymysql.Error as e:
        print(f"Error retrieving achievement records: {e}")
    except ValueError:
        print("Please enter valid numeric values.")
    except Exception as e:
        print(f"Unexpected error: {e}")