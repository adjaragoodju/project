from functools import wraps
from flask import redirect, url_for, session, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Вы должны войти в систему, чтобы увидеть эту страницу", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function