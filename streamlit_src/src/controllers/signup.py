from src.models.session import Session

def signup(login, mdp):
    s = Session(login,mdp)
    
    s.signin()
    s.login()
    if s.logged:
        s.persist()
        return True
    else:
        return False