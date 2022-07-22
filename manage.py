import os

import click
from flask_migrate import Migrate

from interview import create_app, db
from interview.models import Answer, Interview, Question, Role, User

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.cli.command("create-recruiter")
@click.argument("name")
def create_recruiter(name):
    db.create_all()
    recruiter = Role(role_name=name)
    db.session.add(recruiter)
    db.session.commit()
    user = User(email="recr@r.com", username=name, password="123", role=recruiter)
    db.session.add(user)
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Role=Role,
        Interview=Interview,
        Question=Question,
        Answer=Answer,
    )
