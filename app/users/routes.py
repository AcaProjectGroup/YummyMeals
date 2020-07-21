from flask import render_template, url_for, redirect, flash, request, Blueprint
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from .models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from .. import bcrypt
from .. import db
import os
from PIL import Image
import secrets
from .. meals.models import Meal

satatic_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

users_bp = Blueprint(
    'users',
    __name__,
    template_folder='templates',
    url_prefix='/user',
    static_folder='static',
    static_url_path=satatic_path
)
  

@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html',
                           title='Register', form=form)


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            nest_page = request.args.get('next')
            return redirect(nest_page) if nest_page else redirect(url_for('index.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',
                           title='Login', form=form)


@users_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


def save_prof_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(users_bp.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@users_bp.route('/account', methods=['POST'])
@login_required
def account_post():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        data_not_changed = (current_user.username != form.username.data)
        if not data_not_changed and not form.picture.data:
            flash("No changes", 'success')
        else:
            if data_not_changed:
                current_user.username = form.username.data
                current_user.email = form.email.data
            elif form.picture.data:
                picture_file = save_prof_picture(form.picture.data)
                current_user.image_file = picture_file
            db.session.commit()
            flash("Your account has been updated", 'success')
        return redirect(url_for('users.account_get'))

    return redirect(url_for('users.account_get'))


@users_bp.route('/account', methods=['GET'])
@login_required
def account_get():
    form = UpdateAccountForm()
    form.username.data = current_user.username
    form.email.data = current_user.email
    image_file = url_for('users.static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html',
                           title='Account', image_file=image_file, form=form)

@users_bp.route('/new_recipe', methods=['GET', "POST"])
@login_required
def new_recipe():
    form = PostForm()
    if form.validate_on_submit():
        meal = Post(title=form.title.data, content=form.content.data)
        print(meal)

        # nerqevi masy vorpes orinaka te vonc kara database um avelacni
    #if form.validate_on_submit():
    #    post = Post(title=form.title.data, content=form.content.data, author=current_user)
    #    db.session.add(post)
    #    db.session.commit()
    #    flash('Your post has been created!', 'success')
    #    return redirect(url_for('index'))
    return render_template('new_recipe.html',
                           title='New Post', form=form, legend='New Post')

