from mariadb import *
from sys import exit
import mariadb

class MariaConnection:
    def __init__(self, attributes):
        """
        attributes: dict{host:val, port:val, user:val, password:val, database:val}
        """
        try: 
            self.mariaconnection = Connection(**attributes)
            self.mariaconnection.autocommit = True
            self.cursor = Cursor(self.mariaconnection)
        except mariadb.ProgrammingError as e:
            print(e)
            print("Attributes are wrong! Check spelling and that attrs are placed only as [host, port, user, password, database]")
            exit(0)

class Users:
    def __init__(self, mariaconnection: MariaConnection):
        """
        mariaconnection: Mariaconnection object
        """
        self.mariaconnection = mariaconnection
    
    def get_info(self, username):
        self.mariaconnection.cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        info = self.mariaconnection.cursor.fetchall()
        # print(info)
        if info:
            return info
        else:
            return -1
        
    def get_all_users_on_station(self, station_id):
        self.mariaconnection.cursor.execute("SELECT SUM(team_size) FROM users WHERE current_station = ?", [station_id])
        print((self.mariaconnection.cursor.fetchall()))
        print(len(self.mariaconnection.cursor.fetchall()))

        return len(self.mariaconnection.cursor.fetchall())
    
    def set_current(self, username, station):
        self.mariaconnection.cursor.execute("UPDATE users SET current_station = ? WHERE username = ?", [station, username])
    
    def insert(self, username, team_name, team_members, id):
        self.mariaconnection.cursor.execute("INSERT INTO users (username, team_name, team_members, stations, current_station, id) VALUES (?, ?, ?, ?, ?, ?)", (username, team_name, team_members, 0, 0, id))
    
    def team_size(self, username, size):
        self.mariaconnection.cursor.execute("UPDATE users SET team_size = ? WHERE username = ?", [size, username])

    def add(self, username, station):
        self.mariaconnection.cursor.execute("UPDATE users SET stations = (CONCAT(stations, ' ', ?)) WHERE username = ?", [station, username])

    def get_all_0_users(self):
        self.mariaconnection.cursor.execute("SELECT id FROM users WHERE current_station = '0'")
        return self.mariaconnection.cursor.fetchall()
    
    def get_all_resident_users(self):
        self.mariaconnection.cursor.execute("SELECT id FROM users WHERE current_station = '0' AND NOT (stations LIKE '% -1 %')")
        return self.mariaconnection.cursor.fetchall()
    
    def set_current_by_id(self, id, station):
        self.mariaconnection.cursor.execute("UPDATE users SET current_station = ? WHERE id = ?", [station, id])