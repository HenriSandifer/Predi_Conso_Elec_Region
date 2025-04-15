from src.models.session import Session
import json 

def auth(login, mdp):
    s = Session(login,mdp)
    s.login()
    if s.logged:
        s.persist()
        return True
    else:
        return False

def logout():
    data = {      
    "email" : ""
    }
    with open("session.json", 'w') as outfile:
        json.dump(data, outfile)