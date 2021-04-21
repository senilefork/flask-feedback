from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home():
    return redirect('/register')

@app.route('/home')
def home_page():
    return render_template('base.html')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)
        session['username'] = new_user.username
        db.session.add(new_user)
        db.session.commit()
        flash(f'Success! Welcome {new_user.first_name}!', 'success')
        return redirect(f'/user/{new_user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_form(): 

    if "username" in session:
        return redirect(f"/user/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome, {user.first_name}!')
            session['username'] = user.username
            flash(f"Welcome back {user.first_name}!", "success")
            return redirect(f'/user/{user.username}')
        else:
            form.username.errors = ['Invalid username/passowrd']
            flash("Username/Password incorrect", "danger")
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)
    
   

@app.route('/logout')
def logout():
    session.pop('username')
    flash('Goodbye!', "danger")
    return redirect('/login')

@app.route('/user/<username>', methods=["GET", "POST"])
def user_home(username):
    if session['username'] != username:
        flash("Please sign in", "danger")
        return redirect('/login')
    else:
        user = User.query.filter_by(username=username)
        all_feedback = Feedback.query.all()
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.title.data
            username = username
            new_feedback= Feedback(title=title,content=content,username=username)
            db.session.add(new_feedback)
            db.session.commit()
            flash("Feedback added!", "success")
            return redirect(f'/user/{username}')
        return render_template('user_home.html', user=user, form=form, all_feedback=all_feedback)


@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_feedback(id):

    feedback = Feedback.query.get_or_404(id)
    form = FeedbackForm(obj=feedback)
    
    if feedback.username != session['username']:
        return redirect('/login')

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/user/{feedback.username}")
    
    return render_template('edit.html', form=form, feedback=feedback)

@app.route('/delete/<int:id>', methods=["POST"])
def delete(id):
    
    feedback = Feedback.query.get_or_404(id)

    if feedback.username != session['username'] or "username" not in session:
        flash("please login", "danger")
        return redirect(f'/user/{feedback.username}')

    if feedback.username == session["username"]:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "success")
        return redirect(f'/user/{feedback.username}')
    flash("cannot delete post for another user", "danger")
    return redirect(f'/user/{feedback.username}')


    

    