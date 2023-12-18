from flask import Blueprint, render_template
from flask_login import login_required, current_user

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


@BLP_general.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('general/index.html', user=current_user)


@BLP_general.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('general/profile.html', user=current_user)


@BLP_general.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('general/setting.html', user=current_user)


@BLP_general.route('/faq', methods=['GET', 'POST'])
@login_required
def faq():
    return render_template('general/faq.html', user=current_user)


@BLP_general.route('/crypto_dashboard', methods=['GET', 'POST'])
@login_required
def crypto_dashboard():
    return render_template('general/crypto_dashboard.html', user=current_user)


@BLP_general.route('/nft_dashboard', methods=['GET', 'POST'])
@login_required
def nft_dashboard():
    return render_template('general/nft_dashboard.html', user=current_user)


@BLP_general.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    return render_template('general/wallets.html', user=current_user)
