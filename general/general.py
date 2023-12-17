from flask import Blueprint, render_template

BLP_general = Blueprint('BLP_general', __name__,
                        template_folder='templates',
                        static_folder='static')


@BLP_general.route('/')
def index():
    return render_template('index.html')
