from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime, timezone
from urllib.parse import urlsplit
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, EditProfileForm
from app.models import User
from werkzeug.security import generate_password_hash

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Portland 的天氣真好！'
        },
        {
            'author': {'username': 'Susan'},
            'body': '復仇者聯盟電影真的很酷！'
        }
    ]
    return render_template('index.html', title='首頁', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).from_statement(sa.text(f"SELECT * FROM user WHERE username = '{form.username.data}'")))
        if user is None or not user.check_password(form.password.data):
            flash('無效的使用者名稱或密碼')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='登入', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # 錯誤訊息
    username_error = None
    email_error = None
    password_error = None
    password2_error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('re_password')
        db_password = generate_password_hash(password)
        check_name = db.session.scalar(db.select(User).from_statement(db.text(f"SELECT * FROM user WHERE username = '{username}'")))
        check_email = db.session.scalar(db.select(User).from_statement(db.text(f"SELECT * FROM user WHERE email = '{email}'"))) 
        # 表單驗證
        if check_name:
            username_error = "此名稱已有人使用。"
        if check_email:
            email_error = "此信箱已有人使用。"
        if not username:
            username_error = "請填寫使用者名稱"
        if not email:
            email_error = "請填寫郵件地址"
        if not password:
            password_error = "請填寫密碼"
        if not password2:
            password2_error = "再輸入一次密碼"
        # 驗證第二次密碼
        if password and password2 and password != password2:
            password2_error = "密碼錯誤"
            # 驗證通過，新增一筆使用者資料
        elif not (username_error or email_error or password_error or password2_error):
            print("註冊成功")
            new_user = User(username=username, email=email, password_hash=db_password)
            insert_query = db.text("INSERT INTO user (username, email, password_hash, about_me, last_seen) VALUES (:username, :email, :password_hash, :about_me, :last_seen)")
            params = {
                'username': new_user.username,
                'email': new_user.email,
                'password_hash': new_user.password_hash,
                'about_me': new_user.about_me,
                'last_seen': new_user.last_seen
                }
            db.session.execute(insert_query, params)
            db.session.commit()
            flash('恭喜，你現在是一名註冊使用者！')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', username_error=username_error, email_error=email_error, password_error=password_error, password2_error=password2_error)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).from_statement(sa.text(f"SELECT * FROM user WHERE username = '{username}'")))

    posts = [
        {'author': user, 'body': '測試貼文 #1'},
        {'author': user, 'body': '測試貼文 #2'}
    ]
    
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)