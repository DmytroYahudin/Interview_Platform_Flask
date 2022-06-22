import os
from interview import create_app, db

from interview.models import User, Role, Interview, Question, Answer
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                User=User,
                Role=Role,
                Interview=Interview,
                Question=Question,
                Answer=Answer)
