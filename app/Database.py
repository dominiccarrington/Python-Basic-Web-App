"""
Basic Python Web Application
Copyright (C) 2017 Dominic Carrington

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3

class Database:
    _instance = None

    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    @staticmethod
    def get_instance(database=None):
        if Database._instance is None:
            if database is None:
                raise ValueError()
            Database._instance = Database(database)

        return Database._instance

    def newQuery(self):
        return Database.Query()

    def close(self):
        self.cursor.close()
        self.conn.close()

    class Query:
        def __init__(self):
            self.db = Database.get_instance()
            self.table = ""
            self.query = ""
            self.where_num = 0
            self.action = False
            self.executed = False
            self.hidden = {}

        def _action(self, action, table):
            self.action = True
            self.table = table
            self.query = action + " FROM `" + table + "`"
            return self

        def select(self, table, *attr):
            attrs = "*"
            if attr:
                attrs = "`"
                attrs += "`,`".join(attr)
                attrs += "`"
                attrs = attrs.replace(".", "`.`")
            return self._action("SELECT " + attrs, table)

        def delete(self, table):
            return self._action("DELETE", table)

        def join(self, foreign_table, foreign_key, local_key):
            self.query += " JOIN `" + foreign_table + "` ON " + foreign_table + "." + foreign_key + " = " + self.table + "." + local_key
            return self
        
        def insert(self, table, values):
            if isinstance(values, dict):
                values = dict(values)
                attrs = "`" + "`, `".join(list(values.keys())) + "`"
                placeholders = ','.join([":" + key for key in values.keys()])
                self.hidden = values
            elif isinstance(values, list):
                values = list(values)
                keys = None
                for v in values:
                    if not isinstance(v, dict):
                        raise TypeError("All items in the list but be dictionaries")

                    if keys is None:
                        keys = v.keys()

                    if keys != None and keys != v.keys():
                        raise ValueError("All dictionaries must have the same keys")

                attrs = "`" + "`, `".join(list(keys)) + "`"
                placeholders = ','.join([":" + key for key in keys])

            self.query = "INSERT INTO `{}`({}) VALUES ({})".format(table, attrs, placeholders)

            if self.hidden is None:
                self.execute()
            else:
                self.repeatExecute(values)

        def update(self, table, values):
            if not isinstance(values, dict):
                raise TypeError("Values must be a dictionary")
            x = 1
            s = ""
            for k in values.keys():
                s += "`{}` = :{}".format(k, k)

                if x < len(values):
                    s += ","
                x += 1

            self.query = "UPDATE {} SET {}".format(table, s)
            self.hidden = values
            return self

        def where(self, params=(), prefix=" WHERE"):
            if len(params) == 3 and params[1] in ['=', '!=', '>', '<', '>=', '<=']:
                attr = params[0]
                op = params[1]
                value = params[2]

                self.query += prefix + " (`{}` {} :where_{})".format(attr, op, str(self.where_num))
                self.hidden["where_" + str(self.where_num)] = value
                self.where_num += 1
                return self

            return False

        def andWhere(self, params=()):
            return self.where(params, " AND")

        def orWhere(self, params=()):
            return self.where(params, " OR")

        def execute(self):
            self.query += ";"
            self.db.cursor.execute(self.query, self.hidden)
            self.db.conn.commit()
            return self.db.cursor

        def repeatExecute(self, values):
            self.query += ";"
            self.db.cursor.executemany(self.query, values)
            self.db.conn.commit()
            return self.db.cursor

        def fetchAll(self):
            return self.execute().fetchall()

        def fetchOne(self):
            return self.execute().fetchone()

def main():
    db = Database.get_instance("music.db")
    b = db.newQuery()

    tracks = b.select("track", "track.title", "artist.name").join("artist", "id", "artist_id").fetchAll()
    del b

    for track in tracks:
        print(track)

if __name__ == "__main__":
    main()
