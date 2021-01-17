import pymysql.cursors
import json
import datetime
from datetime import timezone

class DailyScore:
    def __init__(self, user_id, score, date_created):
        self.user_id = user_id
        self.score = score
        self.date_created = date_created
    
    def __str__(self):
        return "{'user_id':" + str(self.user_id) + ", 'score':" + str(self.score) + ", 'date_created':'" + self.date_created.strftime("%Y-%m-%dT%H:%M:%SZ") + "'}"
    
    def __getitem__(self, n):
        if n == "user_id": return self.user_id
        if n == "score": return self.score
        if n == "date_created": return self.date_created

class User:
    def __init__(self, user_id=None, email=None, dbx=None, friends=True):
        self.user_id = user_id
        self.email = email
        self.dbx = dbx
        self.friends = friends
        
        self.exists = True
        
        self.user = self.getUser()
        self.json = self.toJson()
    
    def getUser(self):
        c = self.dbx.cursor()
        if self.email != None:
            c.execute("SELECT users.user_id, users.name, users.email, users.password, users.date_created, GROUP_CONCAT(DISTINCT friends.user_id1 SEPARATOR ',') FROM users JOIN friends ON (users.user_id = friends.user_id1 OR users.user_id = friends.user_id2) WHERE email='" + self.email + "'")
            
            m = c.fetchall()
            if not ("GROUP_CONCAT(DISTINCT friends.user_id1 SEPARATOR ',')" in m[0]) and not ("GROUP_CONCAT(DISTINCT friends.user_id2 SEPARATOR ',')" in m[0]):
                c.execute("SELECT users.user_id, users.name, users.email, users.password, users.date_created, GROUP_CONCAT(DISTINCT friends.user_id2 SEPARATOR ',') FROM users JOIN friends ON users.user_id = friends.user_id1 WHERE email='" + self.email + "' UNION ALL SELECT users.user_id, users.name, users.email, users.password, users.date_created, GROUP_CONCAT(DISTINCT friends.user_id1 SEPARATOR ',') FROM users JOIN friends ON users.user_id = friends.user_id2 WHERE email='" + self.email + "'")
            
            if m[0]["GROUP_CONCAT(DISTINCT friends.user_id1 SEPARATOR ',')"] == None or m[0]["GROUP_CONCAT(DISTINCT friends.user_id2 SEPARATOR ',')"] == None:
                c.execute("SELECT users.user_id, users.name, users.email, users.password, users.date_created FROM users WHERE email='" + self.email + "'")
                self.friends = False
        
        if self.user_id != None:
            c.execute("SELECT users.user_id, users.name, users.email, users.password, users.date_created, GROUP_CONCAT(DISTINCT friends.user_id2 SEPARATOR ',') FROM users JOIN friends ON users.user_id = friends.user_id1 WHERE users.user_id='" + str(self.user_id) + "' UNION ALL SELECT users.user_id, users.name, users.email, users.password, users.date_created, GROUP_CONCAT(DISTINCT friends.user_id1 SEPARATOR ',') FROM users JOIN friends ON users.user_id = friends.user_id2 WHERE users.user_id='" + str(self.user_id) + "'")
        
        out = c.fetchall()
        
        if len(out) == 0:
            self.exists = False
            return
        
        if self.friends:
            result = [out[0][0], out[0][1], out[0][2], out[0][3], out[0][4], [User(user_id=int(out[0][5]), dbx=self.dbx, friends=False)], []]
        
            if len(out) > 1:
                for i in range(1, len(out)):
                    result[5].append(User(user_id=int(out[i][5]), dbx=self.dbx, friends=False))
        else:
            if 'user_id' in out[0]:
                result = [out[0]['user_id'], out[0]['name'], out[0]['email'], out[0]['password'], out[0]['date_created'], [], []]
            else:
                result = [out[0][0], out[0][1], out[0][2], out[0][3], out[0][4], [], []]
        
        c.execute("SELECT dailyscore.score, dailyscore.date_created FROM users JOIN dailyscore ON users.user_id = dailyscore.user_id WHERE dailyscore.user_id = " + str(result[0]) + " ORDER BY dailyscore.date_created")
        
        out = c.fetchall()[::-1][:14]
        
        for t in out:
            result[6].append(DailyScore(result[0], t[0], t[1]))
            
        result[4] = result[4].strftime("%Y-%m-%dT%H:%M:%S-09:00")
        
        return result
        
    def toJson(self):
        if self.exists == False: return {}
        if len(self.user[6]) == 0:
            return {"id":self.user[0], "name":self.user[1], "email":self.user[2], "password":self.user[3], "date_created":self.user[4], "friends":self.user[5], "scores":self.user[6], 'avgScore':0}
        return {"id":self.user[0], "name":self.user[1], "email":self.user[2], "password":self.user[3], "date_created":self.user[4], "friends":self.user[5], "scores":self.user[6], 'avgScore':(sum([i["score"] for i in self.user[6]])/len(self.user[6]))}
    
    def __str__(self):
        if not self.exists: return "{}"
        
        if self.friends:
            return "{'id':" + str(self.user[0]) + ", 'name': '" + self.user[1] + "', 'email': '" + self.user[2] + "', password': '" + self.user[3] + "', date_created': '" + self.user[4] + "', friends': [" + ' '.join([str(i) for i in self.user[5]]) + "], scores': '" + ' '.join([str(i) for i in self.user[6]]) + "', 'avgScore':" + str(round(sum([i["score"] for i in self.user[6]])/len(self.user[6]), 2)) + "}"
        else:
            if len(self.user[6]) == 0:
                return "{'id': " + str(self.user[0]) + ", 'name': '" + self.user[1] + "', 'email': '" + self.user[2] + "', password': '" + self.user[3] + "', date_created': '" + self.user[4] + ", scores': [], 'avgScore': 0}"
            
            return "{'id':" + str(self.user[0]) + ", 'name': '" + self.user[1] + "', 'email': '" + self.user[2] + "', password': '" + self.user[3] + "', date_created': '" + self.user[4] + ", scores': '" + ' '.join([str(i) for i in self.user[6]]) + "', 'avgScore':" + str((round(sum([i["score"] for i in self.user[6]])/len(self.user[6]), 2)) if len(self.user[6]) > 0 else 0) + "}"

class database:
    def __init__(self):
        self.dbx = pymysql.connect(
            host="localhost", port=8889,
            user="MyCovidScore", password="covid19",
            database="MyCovidScore",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True
        )
    
    def getUser(self, email):
        return User(email=email, dbx=self.dbx)
    
    def query_db(self, query, data=None):
        with self.dbx.cursor() as cursor:
            try:
                executable = cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except Exception as e:
                print("Something went wrong", e)
                return False    

def main():
    db = database()
    b = db.getUser("rtsfred@gmail.com")
    print(b)
    print(b.json)

if __name__ == '__main__': main()