import os
import pymysql
import pymysql.cursors

# Import modules for different tables
import stadium
import tactic
import managers
import clubs
import players
import leagues
import leaguedetails
import matchx
import contracts
import playernationality
import playerlanguagespoken
import playerpositionsplayed
import playsin
import youthplayer
import captain
import loanplayer
import injuryrecord
import recoveryprediction
import playermatchperformance
import managermatchperformance
import managerachievements
import managernationality

def clear():
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/macOS
        os.system('clear')
        
def addRecord(ch2, con, cur):
    """
    Add a record to the specified table
    """
    table_modules = {
        1: stadium,
        2: tactic,
        3: managers,
        4: clubs,
        5: players,
        6: leagues,
        7: leaguedetails,
        9: matchx,
        10: contracts,
        11: playernationality,
        12: playerlanguagespoken,
        13: playerpositionsplayed,
        14: playsin,
        15: youthplayer,
        16: captain,
        17: loanplayer,
        18: injuryrecord,
        19: recoveryprediction,
        20: playermatchperformance,
        21: managermatchperformance,
        22: managerachievements,
        23: managernationality
    }
    
    if ch2 in table_modules:
        table_modules[ch2].addRecord(con, cur)
    else:
        print("Invalid table selection for adding record")

def deleteRecord(ch2, con, cur):
    """
    Delete a record from the specified table
    """
    table_modules = {
        1: stadium,
        2: tactic,
        3: managers,
        4: clubs,
        5: players,
        6: leagues,
        7: leaguedetails,
        8: matchx,
        9: contracts,
        10: playernationality,
        11: playerlanguagespoken,
        12: playerpositionsplayed,
        13: playsin,
        14: youthplayer,
        15: captain,
        16: loanplayer,
        17: injuryrecord,
        18: recoveryprediction,
        19: playermatchperformance,
        20: managermatchperformance,
        21: managerachievements,
        22: managernationality
    }
    
    if ch2 in table_modules:
        table_modules[ch2].deleteRecord(con, cur)
    else:
        print("Invalid table selection for deleting record")

def updateRecord(ch2, con, cur):
    """
    Update a record in the specified table
    """
    table_modules = {
        1: stadium,
        2: tactic,
        3: managers,
        4: clubs,
        5: players,
        6: leagues,
        7: leaguedetails,
        8: matchx,
        9: contracts,
        10: playernationality,
        11: playerlanguagespoken,
        12: playerpositionsplayed,
        13: playsin,
        14: youthplayer,
        15: captain,
        16: loanplayer,
        17: injuryrecord,
        18: recoveryprediction,
        19: playermatchperformance,
        20: managermatchperformance,
        21: managerachievements,
        22: managernationality
    }
    
    if ch2 in table_modules:
        table_modules[ch2].updateRecord(con, cur)
    else:
        print("Invalid table selection for updating record")

def retrieveRecord(ch2, con, cur):
    """
    Retrieve records from the specified table
    """
    table_modules = {
        1: stadium,
        2: tactic,
        3: managers,
        4: clubs,
        5: players,
        6: leagues,
        7: leaguedetails,
        8: matchx,
        9: contracts,
        10: playernationality,
        11: playerlanguagespoken,
        12: playerpositionsplayed,
        13: playsin,
        14: youthplayer,
        15: captain,
        16: loanplayer,
        17: injuryrecord,
        18: recoveryprediction,
        19: playermatchperformance,
        20: managermatchperformance,
        21: managerachievements,
        22: managernationality
    }
    
    if ch2 in table_modules:
        table_modules[ch2].retrieveRecord(con, cur)
    else:
        print("Invalid table selection for retrieving record")

def dispatch(ch1, ch2, con, cur):
    """
    Function that maps helper functions to option entered
    """
    try:
        if ch1 == 1:
            addRecord(ch2, con, cur)
        elif ch1 == 2:
            deleteRecord(ch2, con, cur)
        elif ch1 == 3:
            updateRecord(ch2, con, cur)
        elif ch1 == 4:
            retrieveRecord(ch2, con, cur)
        else:
            print("Error: Invalid Option")
        
        # Commit changes after each operation
        con.commit()
        
        # Wait for user to press enter
        input("Press Enter to continue...")
    
    except Exception as e:
        # Rollback in case of error
        con.rollback()
        print(f"An error occurred: {e}")
        input("Press Enter to continue...")

# Main program
def main():
    while True:
        try:
            # Clear screen (works for both Unix and Windows)
            clear()

            # Database connection
            con = pymysql.connect(
                host='localhost',
                port=3306,
                user="root",
                password="678007",
                db='Football',
                cursorclass=pymysql.cursors.DictCursor
            )

            if con.open:
                print("Connected to database")
            else:
                print("Failed to connect")

            input("Press Enter to continue...")

            with con.cursor() as cur:
                while True:
                    # Clear screen
                    clear()

                    # Main menu
                    print("1. Add a record")
                    print("2. Delete a record")
                    print("3. Update a record")
                    print("4. Retrieve a record")
                    print("5. Logout")
                    
                    ch1 = int(input("Enter choice> "))

                    if ch1 == 5:
                        break

                    # Table selection menu
                    print("\nSelect Table to Operate on")
                    print("1. Stadiums")
                    print("2. Tactics")
                    print("3. Managers")
                    print("4. Clubs")
                    print("5. Players")
                    print("6. Leagues")
                    print("7. LeagueDetails")
                    print("8. MatchX")
                    print("9. Contracts")
                    print("10. PlayerNationality")
                    print("11. PlayerLanguageSpoken")
                    print("12. PlayerPositionsPlayed")
                    print("13. PlaysIn")
                    print("14. YouthPlayer")
                    print("15. Captain")
                    print("16. LoadPlayer")
                    print("17. InjuryRecord")
                    print("18. RecoveryPrediction")
                    print("19. PlayerMatchPerformance")
                    print("20. ManagerMatchPerformance")
                    print("21. ManagerAchievements")
                    print("22. ManagerNationality")
                    
                    ch2 = int(input("Enter choice> "))
                    
                    # Dispatch to appropriate function
                    dispatch(ch1, ch2, con, cur)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Connection Refused: Either username or password is incorrect or user doesn't have access to database")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()