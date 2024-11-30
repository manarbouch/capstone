from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash, session
from app import db, create_app  # Import db and create_app from app.py
from models import User, RiskAssessment
from flask_bcrypt import Bcrypt
import matplotlib.pyplot as plt
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from datetime import datetime
import os

# Initialize Flask app using the factory function
app = create_app()
app.config['DEBUG'] = True
app.config['ENV'] = 'development'

bcrypt = Bcrypt(app)  # Initialize Bcrypt with app

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Load user for login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Blueprint
main_blueprint = Blueprint('main', __name__)

# Existing routes
@main_blueprint.route('/')
def index():
    return render_template('index.html')

@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            if user.completed_questionnaire:
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.result'))
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')


@main_blueprint.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash("Email already in use. Please log in.")
            return redirect(url_for('main.login'))

        user = User(email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now complete the questionnaire.')

        # Automatically log in the user after account creation
        login_user(user)

        # Redirect to the result page (where they can complete the questionnaire)
        return redirect(url_for('main.result'))

    return render_template('create_account.html')


@main_blueprint.route('/result', methods=['GET', 'POST'])
def result():
    if not current_user.is_authenticated:
        flash("You need to log in to complete the questionnaire.")
        return redirect(url_for('main.login'))

    user = current_user  # Use current_user from Flask-Login

    if request.method == 'POST':
        goal = request.form['goal']
        time_horizon = request.form['time_horizon']
        reaction = request.form['reaction']
        savings_rate = request.form['savings_rate']
        experience = request.form['experience']

        # Calculate the risk score
        risk_score = calculate_risk_score(goal, time_horizon, reaction, savings_rate, experience)
        risk_category = categorize_risk(risk_score)

        # Save the risk assessment
        risk_assessment = RiskAssessment(
            user_id=user.id,
            goal=goal,
            time_horizon=time_horizon,
            reaction=reaction,
            savings_rate=savings_rate,
            experience=experience,
            risk_score=risk_score,
            risk_category=risk_category
        )

        # Mark the user as having completed the questionnaire
        user.completed_questionnaire = True
        db.session.add(risk_assessment)
        db.session.commit()

        flash("Questionnaire completed successfully!")
        return redirect(url_for('main.dashboard'))  # Redirect to dashboard after questionnaire completion

    return render_template('result.html')

# Dashboard route
@main_blueprint.route('/dashboard')
@login_required
def dashboard():
    user = current_user  # Use current_user from Flask-Login

    # Fetch risk assessments for the user
    risk_assessments = RiskAssessment.query.filter_by(user_id=user.id).all()

    if not risk_assessments:
        flash("No risk assessments found.")
        return redirect(url_for('main.result'))  # Redirect to risk assessment if none found

    # Collecting risk scores and time horizon for the chart
    time_labels = [ra.created_at.strftime('%Y-%m-%d') for ra in risk_assessments]
    risk_scores_over_time = [ra.risk_score for ra in risk_assessments]

    # Data for bar chart
    goals = ['growth', 'income', 'preservation']
    goal_counts = {goal: 0 for goal in goals}
    for ra in risk_assessments:
        if ra.goal in goal_counts:
            goal_counts[ra.goal] += 1

    bar_labels = list(goal_counts.keys())
    bar_values = list(goal_counts.values())

    # Render template with data
    return render_template(
        'dashboard.html',
        user=user,
        time_labels=time_labels,
        risk_scores_over_time=risk_scores_over_time,
        bar_labels=bar_labels,
        bar_values=bar_values
    )

# Additional routes
@main_blueprint.route('/profile')
def profile():
    return render_template('profile.html')

@main_blueprint.route('/notifications')
def notifications():
    return render_template('notifications.html')

@main_blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Get data from the form
        name = request.form.get('name')
        password = request.form.get('password')

        # Update name
        current_user.name = name

        # If a password is provided, hash and update it
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            current_user.password = hashed_password

        # Commit changes to the database
        db.session.commit()

        flash('Your information has been updated successfully!', 'success')

        return redirect(url_for('main.settings'))

    return render_template('settings.html')


@main_blueprint.route('/risk_assessment')
def risk_assessment():
    return render_template('risk_assessment.html')

@main_blueprint.route('/risk_assessment', methods=['GET', 'POST'], endpoint='risk_assessment_v2')
def risk_assessment_v2():
    if request.method == 'POST':
        # Extract the form data
        age = request.form.get('age')
        financial_goals = request.form.get('financial_goals')
        investment_experience = request.form.get('investment_experience')

        # Calculate risk score (this is just an example logic)
        risk_score = 0

        # Simple risk calculation based on age and experience (this can be improved)
        if age and int(age) > 40:
            risk_score += 10  # Lower risk for older individuals
        else:
            risk_score += 20  # Higher risk for younger individuals

        if financial_goals == 'retirement':
            risk_score += 30
        elif financial_goals == 'long_term':
            risk_score += 20
        else:
            risk_score += 10

        if investment_experience == 'beginner':
            risk_score -= 10
        elif investment_experience == 'intermediate':
            risk_score += 10
        else:
            risk_score += 20

        # Create a new RiskAssessment entry in the database
        new_risk_assessment = RiskAssessment(
            user_id=current_user.id,  # Assume current_user is being managed by Flask-Login
            goal=financial_goals,
            time_horizon="Unknown",  # Add logic for time horizon if needed
            reaction="Unknown",  # Add logic for reaction if needed
            savings_rate="Unknown",  # Add savings rate input if needed
            experience=investment_experience,
            risk_score=risk_score,
            created_at=datetime.utcnow()
        )

        db.session.add(new_risk_assessment)
        db.session.commit()

        # Flash a success message or any other result
        flash(f'Your risk score is {risk_score}.', 'success')

        # Redirect or render the result page
        return render_template('result.html', risk_score=risk_score, financial_goals=financial_goals,
                               investment_experience=investment_experience)

    # If the method is GET, just show the form
    return render_template('risk_assessment.html')

# Logout route
@main_blueprint.route('/logout')
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('main.index'))

# Function to calculate risk score
def calculate_risk_score(goal, time_horizon, reaction, savings_rate, experience):
    score = 0

    # Financial goal
    if goal == 'growth':
        score += 25
    elif goal == 'income':
        score += 15
    elif goal == 'preservation':
        score += 5

    # Time Horizon
    if time_horizon == 'long':
        score += 20
    elif time_horizon == 'medium':
        score += 15
    elif time_horizon == 'short':
        score += 10

    # Reaction to market decline
    if reaction == 'buy_more':
        score += 25
    elif reaction == 'wait':
        score += 15
    elif reaction == 'sell':
        score += 5

    # Savings rate
    if savings_rate == 'high':
        score += 15
    elif savings_rate == 'moderate':
        score += 10
    elif savings_rate == 'low':
        score += 5

    # Experience level
    if experience == 'expert':
        score += 20
    elif experience == 'intermediate':
        score += 10
    elif experience == 'beginner':
        score += 5

    return score

# Risk category function
def categorize_risk(risk_score):
    if risk_score >= 80:
        return 'High Risk'
    elif 60 <= risk_score < 80:
        return 'Moderate Risk'
    else:
        return 'Low Risk'

# Investment suggestion function
def get_investment_suggestions(risk_category, financial_goals):
    suggestions = []

    if risk_category == 'High Risk':
        suggestions.append("Consider high-risk investments such as stocks or growth funds.")
    elif risk_category == 'Moderate Risk':
        suggestions.append("Consider balanced investments such as index funds or bonds.")
    else:
        suggestions.append("Consider low-risk investments such as bonds or dividend stocks.")

    if financial_goals == 'growth':
        suggestions.append("Invest in growth stocks or real estate.")
    elif financial_goals == 'income':
        suggestions.append("Consider dividend stocks or rental properties.")
    else:
        suggestions.append("Consider safer investments like bonds or certificates of deposit (CDs).")

    return suggestions


@main_blueprint.route('/investment_suggestions')
@login_required
def investment_suggestions():
    user = current_user  # Use current_user from Flask-Login

    # Check if the user has completed the questionnaire and has a risk assessment
    latest_assessment = RiskAssessment.query.filter_by(user_id=user.id).order_by(
        RiskAssessment.created_at.desc()).first()

    if not latest_assessment:
        flash("You need to complete the risk assessment to view investment suggestions.")
        return redirect(url_for('main.result'))  # Redirect to risk assessment page if no assessment is found

    # Get investment suggestions based on the latest risk assessment
    risk_category = latest_assessment.risk_category
    investment_suggestions = get_investment_suggestions(risk_category, latest_assessment.goal)

    return render_template('investment_suggestions.html', investment_suggestions=investment_suggestions)


# Register the blueprint
app.register_blueprint(main_blueprint, url_prefix='/')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
