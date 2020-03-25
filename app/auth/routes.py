from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app import db_handlers
from app.auth import bp
from app.auth.forms import RegistrationForm, LoginForm, EditProfileForm
from app.models import User
import folium
import os


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect

    start_coords = (50.4547, 30.524)
    m = folium.Map(width=300, height=300, location=start_coords, zoom_start=12)
    folium.Marker(
        location=[50.4547, 30.520],
        popup='your location',
        icon=folium.Icon(color='green'),
        draggable=True
    ).add_to(m)
    m.save('app/templates/_map.html')
    return render_template('register.html', title='Register', form=form)
