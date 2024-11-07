from app.exceptions import DbEntityAlreadyExists


class AccountEntityAlreadyExist(DbEntityAlreadyExists):
    @property
    def entity_name(self):
        return "Account"
