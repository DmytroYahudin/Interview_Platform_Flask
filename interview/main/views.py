from datetime import datetime
from flask import render_template, session, redirect, url_for
from flask_login import login_required, current_user
from collections import namedtuple
from . import main
from .forms import NameForm, InterviewerRegistrationForm, InterviewForm, QuestionForm, CandidateForm, AnswerForm
from .. import db
from ..models import User, Role, Candidate, Question, Interview, Answer


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())


@main.route('/interviewers/')
def list_of_interviewers():
    role = Role.query.filter_by(role_name='interviewer').first()
    interviewer_list = User.query.filter_by(role_id=role.id)
    return render_template('interviewers.html', interviewers=interviewer_list)


@main.route('/interviews/')
def interviews():
    interviews_list = Interview.query.all()
    return render_template('interviews.html', interviews_list=interviews_list)


@main.route('/add_interviewers/', methods=['GET', 'POST'])
def add_interviewer():
    form = InterviewerRegistrationForm()
    role = Role.query.filter_by(role_name='interviewer').first()
    if form.validate_on_submit():
        interviewer = User(email=form.email.data,
                           username=form.username.data,
                           password=form.password.data,
                           role_id=role.id)
        db.session.add(interviewer)
        db.session.commit()
        return redirect(url_for('.list_of_interviewers'))
    return render_template('auth/register.html', form=form)
    pass


@main.route('/questions/')
def list_of_questions():
    questions_list = Question.query.order_by(Question.weight.asc())
    return render_template('questions.html', questions=questions_list)
    pass


@main.route('/add_question/', methods=['GET', 'POST'])
def add_question():
    form = QuestionForm()
    if form.validate():
        if form.weight:
            question = Question(question_text=form.question_text.data,
                                weight=form.weight.data)
        else:
            question = Question(question_text=form.question_text.data)
        db.session.add(question)
        db.session.commit()
        questions_list = Question.query.order_by(Question.weight.asc())
        return render_template('questions.html', questions=questions_list)
    return render_template('add_question.html', form=form)


@main.route('/add_candidate/', methods=['GET', 'POST'])
def add_candidate():
    form = CandidateForm()
    if form.validate():
        candidate = Candidate(first_name=form.first_name.data,
                              last_name=form.last_name.data,
                              email=form.email.data,
                              skills=form.skills.data,
                              about=form.about.data)
        db.session.add(candidate)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('add_candidate.html', form=form)


@main.route('/add_interview/', methods=['GET', 'POST'])
def add_interview():
    form = InterviewForm()

    form.candidate_id.query = db.session.query(Candidate)
    form.interviewer.query = db.session.query(User)
    form.question.query = db.session.query(Question)

    if form.validate_on_submit():

        candidate_id = form.candidate_id.data
        interviewer = form.interviewer.data
        question = form.question.data

        interv = Interview(
            candidate_id=candidate_id.id,
            interviewer=interviewer,
            question=question,
        )
        db.session.add(interv)
        db.session.commit()

        return redirect(url_for('.index'))
    return render_template('add_interview.html', form=form)


@main.route('/start_interview/<int:id>', methods=['GET', 'POST'])
def start_interview(id):
    interview = Interview.query.filter_by(id=id).first()
    questions = interview.question

    marks = [dict(mark=None) for _ in questions]
    form = AnswerForm(mark_set=marks)

    if form.validate_on_submit():
        mark_set_by = current_user._get_current_object()

        total_mark = 0
        for i in range(questions.count()):
            question_id = questions[i].id
            mark = form.mark_set.data[i]['mark']
            answer = Answer(mark=mark,
                            interview_id=Interview.query.filter_by(id=id),
                            mark_set_by=[mark_set_by],
                            question_id=question_id)

            total_mark += questions[i].weight * mark
            db.session.add(answer)

        interview.total_mark = total_mark
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('answer.html', form=form, questions=questions)
