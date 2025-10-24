from create_table.create_session import db, fernet


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BIGINT, primary_key=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(60), nullable=True)
    status = db.Column(db.Integer, default=0)
    date_of_key = db.Column(db.DateTime, nullable=True)
    expire_date = db.Column(db.Integer, nullable=True)
    _state_with_token = db.Column("state", db.Text, nullable=True)
    _access_token_encrypted = db.Column("access_token" ,db.Text(), nullable=True)
    _refresh_token_encrypted = db.Column("refresh_token" ,db.Text(), nullable=True)

    selected = db.relationship("Selected", secondary = 'users_selected', back_populates="users")


    @property
    def state(self):
        if self._state_with_token:
            return fernet.decode(self._state_with_token.encode()).decode()
        return None

    @state.setter
    def state(self, value):
        if value:
            self._state_with_token = fernet.encode(value.encode()).decode()
        else:
            self._state_with_token = None


    @property
    def access_token(self):
        if self._access_token_encrypted:
            return fernet.decrypt(self._access_token_encrypted.encode()).decode()
        return None
    @access_token.setter
    def access_token(self, value):
        if value:
            self._access_token_encrypted = fernet.encrypt(value.encode()).decode()
        else:
            self._access_token_encrypted = None

    @property
    def refresh_token(self):
        if self._refresh_token_encrypted:
            return fernet.decrypt(self._refresh_token_encrypted.encode()).decode()
        return None
    @refresh_token.setter
    def refresh_token(self, value):
        if value:
            self._refresh_token_encrypted = fernet.encrypt(value.encode()).decode()
        else:
            self._refresh_token_encrypted = None


class Selected(db.Model):
    __tablename__ = 'selected'
    select_user_id = db.Column(db.BIGINT,primary_key=True ,nullable=False)
    link = db.Column(db.Text, nullable=False)

    users = db.relationship("Users", secondary = 'users_selected', back_populates = 'selected' )


class UsersSelected(db.Model):
    __tablename__ = 'users_selected'
    users_id = db.Column(db.BIGINT, db.ForeignKey('users.id'),primary_key=True , nullable=False)
    selected_id = db.Column(db.BIGINT, db.ForeignKey('selected.select_user_id'),primary_key=True , nullable=False)
    is_favourite = db.Column(db.Boolean, nullable=True)

