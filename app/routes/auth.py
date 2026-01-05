"""
Rotas de autenticação (login, registro, logout)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

from app.extensions import db
from app.models import User, InvitationCode, Level
from app.forms import BaseForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = BaseForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('auth.login'))
        
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('user.index'))
        flash('Email ou senha inválidos.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = BaseForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('auth.register'))
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        invitation_code = request.form['invitation_code']
        
        invitation = InvitationCode.query.filter_by(code=invitation_code, used=False).first()
        if not invitation:
            flash('Código de convite inválido ou já utilizado.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já registrado.', 'error')
            return redirect(url_for('auth.register'))
        
        initial_level = Level.query.order_by(Level.min_points).first()
        if not initial_level:
            flash('Erro de sistema: Nenhum nível inicial encontrado. Contate o administrador.', 'error')
            return redirect(url_for('auth.register'))
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            is_admin=False,
            level_id=initial_level.id
        )
        db.session.add(user)
        db.session.commit()
        
        invitation.used = True
        invitation.used_by_user_id = user.id
        db.session.commit()
        
        flash('Registro concluído! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/generate_invitation', methods=['POST'])
@login_required
def generate_invitation():
    """Gera código de convite (apenas admin)"""
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('user.index'))
    
    form = BaseForm()
    if not form.validate_on_submit():
        flash('Erro de validação CSRF.', 'error')
        return redirect(url_for('admin.admin_users'))
    
    code = str(uuid.uuid4())
    invitation = InvitationCode(code=code)
    db.session.add(invitation)
    db.session.commit()
    
    return jsonify({'code': code})
