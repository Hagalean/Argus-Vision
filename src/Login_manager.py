class Login_Manager:
    def __init__(self):
        pass

    def check_credentials(self, email, pw):
        # return True if credentials are correct
        print(email)
        print(pw)
        if email == "w":
            return False
        return True


    def password_reset_reqquest(self, email):
        print(email)
        return True

    def create_account(self, email, pw, name, surname, phone, bday):
        print(email)
        print(pw)
        print(name)
        print(surname)
        print(phone)
        print(bday)
        return True

