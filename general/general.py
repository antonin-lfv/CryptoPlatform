from flask import Blueprint, render_template
from flask_login import login_required

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates/general',
                        static_folder='static')


@BLP_general.route('/')
@login_required
def index():
    return render_template('index2.html')
