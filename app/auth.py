
from flask import Blueprint, render_template, redirect, url_for, request, flash, g, session
from flask_mail import Message
from itsdangerous import SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db, mail, s

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.register'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()

        # Email verification
        token = s.dumps(email, salt='email-confirm')
        msg = Message('Confirm your email', sender='4fyield@gmail.com', recipients=[email])
        link = url_for('auth.confirm_email', token=token, _external=True)
        msg.body = f'Your link is {link}'
        mail.send(msg)

        flash('Please check your email to confirm your registration')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('auth.dashboard'))
        flash('Invalid credentials')
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>Seu token expirou!</h1>'
    
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Conta já confirmada. Faça o Login.')
    else:
        user.confirmed = True
        db.session.commit()
        flash('Conta confirmada. Obrigado!')
    return redirect(url_for('auth.login'))

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first_or_404()
        token = s.dumps(email, salt='password-reset')
        msg = Message('Reset Your Password', sender='4fyield@gmail.com', recipients=[email])
        link = url_for('auth.reset_password', token=token, _external=True)
        msg.body = f'Link para alterar senha {link}'
        mail.send(msg)
        flash('Verifique seu email, enviamos um link para alteração de senha')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html')


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
        print(f"Token successfully decoded: {email}")
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    except Exception as e:
        print(f"Error loading token: {str(e)}")
        return '<h1>Invalid token!</h1>'
    
    user = User.query.filter_by(email=email).first_or_404()
    
    if request.method == 'POST':
        password = request.form.get('password')
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Sua senha foi alterada!')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)


# @auth.route('/reset_password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     try:
#         email = s.loads(token, salt='password-reset', max_age=3600)
#     except SignatureExpired:
#         return '<h1>The token is expired!</h1>'
    
#     user = User.query.filter_by(email=email).first_or_404()
    
#     if request.method == 'POST':
#         password = request.form.get('password')
#         user.password = generate_password_hash(password, method='sha256')
#         db.session.commit()
#         flash('Your password has been updated!')
#         return redirect(url_for('auth.login'))
    
#     return render_template('reset_password.html')

@auth.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return f'<h1>Bem vindo {user.name}!, Você conhece o Mário?</h1>'
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você não está mais logado.')
    return redirect(url_for('auth.login'))

