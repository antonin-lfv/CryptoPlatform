from flask import Blueprint, render_template
from flask_login import login_required

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


@BLP_general.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('general/index2.html')
