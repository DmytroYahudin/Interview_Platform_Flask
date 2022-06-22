from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db
from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64), unique=True)  # change name to role_name
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'Role {self.name}'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'User {self.username}'


interviewers = db.Table('interviewers',
                        db.Column('interview_id', db.Integer, db.ForeignKey('interviews.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
                        )

questions = db.Table('question',
                     db.Column('interview_id', db.Integer, db.ForeignKey('interviews.id')),
                     db.Column('questions_id', db.Integer, db.ForeignKey('questions.id'))
                     )

mark_set_by = db.Table('mark_set_by',
                       db.Column('answers_id', db.Integer, db.ForeignKey('answers.id')),
                       db.Column('users_id', db.Integer, db.ForeignKey('users.id'))
                       )

answer_for_interview = db.Table('answer_for_interview',
                                db.Column('answers_id', db.Integer, db.ForeignKey('answers.id')),
                                db.Column('interview_id', db.Integer, db.ForeignKey('interviews.id'))
                                )


class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    skills = db.Column(db.String(128))
    about = db.Column(db.String(256))
    interview_id = db.relationship('Interview', backref='candidate', lazy='dynamic')

    def __repr__(self):
        return f'Candidate {self.first_name} {self.last_name}'


class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'))
    interviewer = db.relationship('User',
                                  secondary=interviewers,
                                  backref=db.backref('interviews', lazy='dynamic'),
                                  lazy='dynamic')
    question = db.relationship('Question',
                               secondary=questions,
                               backref=db.backref('questions', lazy='dynamic'),
                               lazy='dynamic')
    total_mark = db.Column(db.Float(precision=2), default=0)
    summary = db.Column(db.String(512), nullable=False, default='')

    def __repr__(self):
        return f'{self.question}'


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(256), unique=True)
    weight = db.Column(db.Float(precision=2), default=1)
    question_marks = db.relationship('Answer', backref='question', lazy='dynamic')

    def __repr__(self):
        return f'{self.question_text}'


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer)
    interview_id = db.relationship('Interview',
                                   secondary=answer_for_interview,
                                   backref=db.backref('answer_for_interview', lazy='dynamic'),
                                   lazy='dynamic')
    mark_set_by = db.relationship('User',
                                  secondary=mark_set_by,
                                  backref=db.backref('answers', lazy='dynamic'),
                                  lazy='dynamic')
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

    def __repr__(self):
        return f'{self.mark}'
