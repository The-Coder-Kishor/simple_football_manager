
import os
import pymysql
import pymysql.cursors
from itertools import permutations
from datetime import datetime, timedelta, date
import random
from decimal import Decimal

def schedule_matches(con, cur):
    query_leagues = "SELECT DISTINCT LeagueID FROM playsin"
    cur.execute(query_leagues)
    leagues = cur.fetchall()
    if not leagues:
        print("No leagues found")
        return
    
    for league in leagues:
        league_id = league['LeagueID']

        query_clubs = """
            SELECT c.ClubID, c.ClubName
            FROM playsin p
            JOIN clubs c ON p.ClubID = c.ClubID
            WHERE p.LeagueID = %s
        """
        cur.execute(query_clubs, (league_id))
        clubs = cur.fetchall()
        if not clubs:
            print("No clubs found")
            return

        club_ids = [club['ClubID'] for club in clubs]
        matches = []
        for home, away in permutations(club_ids, 2):
            start_date = datetime.strptime("2024-08-01", "%Y-%m-%d")  # Season start date
            end_date = datetime.strptime("2025-05-31", "%Y-%m-%d")
            random_days = random.randint(0, (end_date - start_date).days)
            match_date = start_date + timedelta(days=random_days)
            matches.append((match_date.date(), None, None, None, home, away, league_id, home))
        insert_query = """
            INSERT INTO matchx (Date, HomeGoals, AwayGoals, NoOfAttendees, HomeTeamID, AwayTeamID, LeagueID, StadiumID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
   
        for match in matches:
            cur.execute(insert_query, match)
        
    con.commit()
def get_unsimulated_matches_till_today_and_simulate(con, cur):
    today = date.today()
    query = """
    SELECT MatchID, HomeTeamID, AwayTeamID, StadiumID
    FROM matchx
    WHERE Date <= %s AND HomeGoals IS NULL AND AwayGoals IS NULL
    """
    cur.execute(query, (today,))
    unsimulated_matches = cur.fetchall()

    for match in unsimulated_matches:
        match_id = match['MatchID']
        home_team_id = match['HomeTeamID']
        away_team_id = match['AwayTeamID']
        stadium_id = match['StadiumID']

        stadium_query = "SELECT Capacity FROM stadiums WHERE StadiumID = %s"
        cur.execute(stadium_query, (stadium_id, ))
        capacity = cur.fetchone()

        home_players_query = "SELECT PlayerID, OverallRating FROM players WHERE ClubID = %s"
        away_players_query = "SELECT PlayerID, OverallRating FROM players WHERE ClubID = %s"

        cur.execute(home_players_query, (home_team_id,))
        home_players = cur.fetchall()

        cur.execute(away_players_query, (away_team_id,))
        away_players = cur.fetchall()

        managers_query = "SELECT ManagerID FROM clubs WHERE ClubID = %s"

        cur.execute(managers_query, (home_team_id,))
        home_manager = cur.fetchone()
        
        cur.execute(managers_query, (away_team_id,))
        away_manager = cur.fetchone()

        home_team_rating = sum(player['OverallRating'] for player in home_players) / len(home_players) if home_players else 70
        away_team_rating = sum(player['OverallRating'] for player in away_players) / len(away_players) if away_players else 70

        home_rating = Decimal(home_team_rating)
        away_rating = Decimal(away_team_rating)

        scaling_factor = 50  # Increase this to reduce the mean
        std_dev = 0.5

        home_goals = max(0, int(random.gauss(float(home_rating) / scaling_factor, std_dev)))
        away_goals = max(0, int(random.gauss(float(away_rating) / scaling_factor, std_dev)))


        update_match_query = """
        UPDATE matchx 
        SET HomeGoals = %s, AwayGoals = %s, NoOfAttendees = %s
        WHERE MatchID = %s
        """
        cur.execute(update_match_query, (home_goals, away_goals, capacity['Capacity'], match_id))


        remaining_home_goals = home_goals
        remaining_home_assists = home_goals
        home_scorers = []
        home_assisters = []

        if home_goals > 0:
            home_scorers = random.choices(range(len(home_players)), k=home_goals)
            home_assisters = random.choices(range(len(home_players)), k=random.randint(0, home_goals))

        for idx, player in enumerate(home_players):
            player_id = player['PlayerID']
            # Generate random performance stats
            pass_accuracy = random.uniform(60, 95)
            distance_covered = random.uniform(8000, 12000)
            minutes_played = random.randint(0, 90)
            goals = home_scorers.count(idx)  # Count how many goals this player scored
            assists = home_assisters.count(idx)  # Count how many assists this player made
            rating = random.uniform(6.0, 8.5) + (goals * 0.5) + (assists * 0.3)  # Adjust rating based on goals/assists

            # Insert player performance
            player_perf_query = """
            INSERT INTO playermatchperformance 
            (PlayerID, MatchID, PassAccuracy, DistanceCovered, MinutesPlayed, Goals, Assists, Ratings)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(player_perf_query, (player_id, match_id, pass_accuracy, distance_covered, 
                                          minutes_played, goals, assists, rating))
        
        remaining_away_goals = away_goals
        remaining_away_assists = away_goals  # Maximum possible assists
        away_scorers = []
        away_assisters = []

        if away_goals > 0:
            # Randomly select goal scorers
            away_scorers = random.choices(range(len(away_players)), k=away_goals)
            # Randomly select assisters (can be less than goals)
            away_assisters = random.choices(range(len(away_players)), k=random.randint(0, away_goals))

        # Simulate away team players
        for idx, player in enumerate(away_players):
            player_id = player['PlayerID']
            pass_accuracy = random.uniform(60, 95)
            distance_covered = random.uniform(8000, 12000)
            minutes_played = random.randint(0, 90)
            goals = away_scorers.count(idx)  # Count how many goals this player scored
            assists = away_assisters.count(idx)  # Count how many assists this player made
            rating = random.uniform(6.0, 8.5) + (goals * 0.5) + (assists * 0.3)  # Adjust rating based on goals/assists

            player_perf_query = """
            INSERT INTO playermatchperformance 
            (PlayerID, MatchID, PassAccuracy, DistanceCovered, MinutesPlayed, Goals, Assists, Ratings)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(player_perf_query, (player_id, match_id, pass_accuracy, distance_covered, 
                                          minutes_played, goals, assists, rating))
        
        cur.execute("SELECT TacticID FROM tactics ORDER BY RAND() LIMIT 2")
        tactics = cur.fetchall()
        team_tactic_id = tactics[0]['TacticID']
        opponent_tactic_id = tactics[1]['TacticID']
        if home_manager:

            manager_perf_query = """
            INSERT INTO managermatchperformance 
            (ManagerID, MatchID, ManagerPerformance, TeamTacticID, OpponentTacticID)
            VALUES (%s, %s, %s, %s, %s)
            """
            # Manager performance influenced by match result
            manager_performance = random.uniform(5.0, 9.0)
            if home_goals > away_goals:
                manager_performance += 1.0
            elif home_goals < away_goals:
                manager_performance -= 1.0
            manager_performance = max(1.0, min(10.0, manager_performance))  # Clamp between 1 and 10
            
            cur.execute(manager_perf_query, (home_manager['ManagerID'], match_id, manager_performance, 
                                           team_tactic_id, opponent_tactic_id))

        if away_manager:
            # Manager performance influenced by match result
            manager_performance = random.uniform(5.0, 9.0)
            if away_goals > home_goals:
                manager_performance += 1.0
            elif away_goals < home_goals:
                manager_performance -= 1.0
            manager_performance = max(1.0, min(10.0, manager_performance))  # Clamp between 1 and 10

            cur.execute(manager_perf_query, (away_manager['ManagerID'], match_id, manager_performance, 
                                           opponent_tactic_id, team_tactic_id))
        con.commit()

def update_league_details(con, cursor):
    cursor.execute("Select LeagueID FROM leagues")
    leagues = cursor.fetchall()
    for league in leagues:
        league_id = league['LeagueID']

        top_scorer_query = """
        SELECT p.PlayerID, p.PlayerName, SUM(pmp.Goals) as TotalGoals
        FROM players p
        JOIN playermatchperformance pmp ON p.PlayerID = pmp.PlayerID
        JOIN matchx m ON pmp.MatchID = m.MatchID
        WHERE m.LeagueID = %s
        GROUP BY p.PlayerID, p.PlayerName
        ORDER BY TotalGoals DESC
        LIMIT 1
        """
        cursor.execute(top_scorer_query, (league_id,))
        top_scorer = cursor.fetchone()

        top_assister_query = """
        SELECT p.PlayerID, p.PlayerName, SUM(pmp.Assists) as TotalAssists
        FROM players p
        JOIN playermatchperformance pmp ON p.PlayerID = pmp.PlayerID
        JOIN matchx m ON pmp.MatchID = m.MatchID
        WHERE m.LeagueID = %s
        GROUP BY p.PlayerID, p.PlayerName
        ORDER BY TotalAssists DESC
        LIMIT 1
        """
        cursor.execute(top_assister_query, (league_id,))
        top_assister = cursor.fetchone()

        clean_sheets_query = """
        WITH GoalkeeperMatches AS (
            SELECT 
                p.PlayerID,
                p.PlayerName,
                m.MatchID,
                m.HomeTeamID,
                m.AwayTeamID,
                m.HomeGoals,
                m.AwayGoals,
                p.ClubID
            FROM players p
            JOIN playerpositionsplayed pp ON p.PlayerID = pp.PlayerID
            JOIN playermatchperformance pmp ON p.PlayerID = pmp.PlayerID
            JOIN matchx m ON pmp.MatchID = m.MatchID
            WHERE pp.Position = 'GK'
            AND m.LeagueID = %s
        ),
        CleanSheets AS (
            SELECT 
                PlayerID,
                PlayerName,
                COUNT(*) as CleanSheetCount
            FROM GoalkeeperMatches gm
            WHERE 
                (gm.ClubID = gm.HomeTeamID AND gm.AwayGoals = 0)
                OR 
                (gm.ClubID = gm.AwayTeamID AND gm.HomeGoals = 0)
            GROUP BY PlayerID, PlayerName
        )
        SELECT PlayerID, PlayerName, CleanSheetCount
        FROM CleanSheets
        ORDER BY CleanSheetCount DESC
        LIMIT 1
        """
        cursor.execute(clean_sheets_query, (league_id,))
        top_clean_sheets = cursor.fetchone()

        update_query = """
        UPDATE leagues 
        SET TopScorerID = %s,
            TopAssistID = %s,
            TopCleanSheetID = %s
        WHERE LeagueID = %s
        """
        
        cursor.execute(update_query, (
            top_scorer['PlayerID'] if top_scorer else None,
            top_assister['PlayerID'] if top_assister else None,
            top_clean_sheets['PlayerID'] if top_clean_sheets else None,
            league_id
        ))

        standings_query = """
        WITH MatchResults AS (
            -- Home team points
            SELECT 
                HomeTeamID as TeamID,
                CASE 
                    WHEN HomeGoals > AwayGoals THEN 3
                    WHEN HomeGoals = AwayGoals THEN 1
                    ELSE 0
                END as Points
            FROM matchx
            WHERE LeagueID = %s
            AND HomeGoals IS NOT NULL
            
            UNION ALL
            
            -- Away team points
            SELECT 
                AwayTeamID as TeamID,
                CASE 
                    WHEN AwayGoals > HomeGoals THEN 3
                    WHEN AwayGoals = HomeGoals THEN 1
                    ELSE 0
                END as Points
            FROM matchx
            WHERE LeagueID = %s
            AND AwayGoals IS NOT NULL
        )
        SELECT TeamID, SUM(Points) as TotalPoints
        FROM MatchResults
        GROUP BY TeamID
        """
        
        cursor.execute(standings_query, (league_id, league_id))
        standings = cursor.fetchall()

        # Update points in playsin table
        for team in standings:
            update_points_query = """
            UPDATE playsin
            SET Points = %s
            WHERE ClubID = %s AND LeagueID = %s
            """
            points = int(team['TotalPoints'])
            cursor.execute(update_points_query, (points, team['TeamID'], league_id))

        # Update winning club (team with most points)
        if standings:
            winning_club_query = """
            SELECT ClubID
            FROM playsin
            WHERE LeagueID = %s
            ORDER BY Points DESC
            LIMIT 1
            """
            cursor.execute(winning_club_query, (league_id,))
            winning_club = cursor.fetchone()

            if winning_club:
                update_winner_query = """
                UPDATE leagues
                SET WinningClubID = %s
                WHERE LeagueID = %s
                """
                cursor.execute(update_winner_query, (winning_club['ClubID'], league_id))
    con.commit()
    

def main():
    con = pymysql.connect(
        host='localhost',
        port=3306,
        user="root",
        password="678007",
        db='Football',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = con.cursor()
    schedule_matches(con, cursor)
    get_unsimulated_matches_till_today_and_simulate(con, cursor)
    update_league_details(con, cursor)

if __name__ == "__main__":
    main()
