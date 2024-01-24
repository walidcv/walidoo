import functools
import  sqlite3
from  werkzeug.security import generate_password_hash,check_password_hash
from flask import Flask,request,redirect,url_for,render_template,flash,session,g

import functools
app = Flask(__name__)
app.config.from_mapping(SECRET_KEY= 'DJSDJDSDJSDBSDELIEEUHEL?dgfghgjghj?NCX?CX')
DATABASE = 'dataB10.db'
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db
# المزخرف ////////////////////////////////
def login_requried(func):
    @functools.wraps(func)
    def wrapped_func(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return func(**kwargs)
    return  wrapped_func
# نهاية المزخرف ////////////////////////////
@app.route('/')
def index():
    # global users_list
    connection = get_db()
    users = connection.execute('SELECT * FROM users').fetchall()
    connection.close()
    return  render_template('home.html',users=users)

# # //////


# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         error = None
#         connection = get_db()
#         user = connection.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
#         connection.commit()
#         connection.close()
#         if not email:
#             error = "البريد غير موجود "
#         elif not user['password']:
#             error = "كلمة المرور خاطئة "
#         if error is None:
#             session.clear()
#             session['id'] = user['id']
#             return redirect(url_for('index'))
#
#         flash(error)
#
#     return render_template('auth/login.html')
# ///////////////////////////////////////////////////////////////
# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        connection = get_db()
        user = connection.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()

        connection.commit()
        connection.close()
        if not email:
            error = "البريد غير موجود "
        elif not check_password_hash(user['pass'],password):
            error = "كلمة المرور خاطئة "
        if error is None:
            session.clear()
            session['id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# //////


#
#
#
@app.route('/user/<int:user_id>')
@login_requried
def show(user_id):
    connection = get_db()
    # emaill = connection.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
    user = connection.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    return render_template('senguser.html', user=user)


@app.route('/pasket/<int:id>')
@login_requried
def pasket(id):
    connection = get_db()
    magal = connection.execute('SELECT * FROM posts WHERE user_id= ?', (id,)).fetchall()
    connection.close()
    return render_template('pasket.html', magal=magal)




@app.route('/delete/<string:id>')
def delete(id):
     connection = get_db()
     cor = connection.cursor()
     cor.execute('DELETE  FROM users WHERE id=?', (id,))
     connection.commit()
     connection.close()
     return redirect(url_for('index'))

@app.route('/update/<string:id>', methods=['GET','POST'])
def update(id):
    # global  users
    if request.method == 'POST':
        connection = get_db()
        cor = connection.cursor()
        username = request.form['username']
        email = request.form['email']
        pas = request.form['pass']
        cor.execute("UPDATE users SET username = ? , email = ? , pass = ?  WHERE id = ?",(username , email , pas , g.user['id']))
        connection.commit()
        connection.close()

        return redirect(url_for('index'))
    return render_template('update.html')





# @app.route('/crt', methods=['GET','POST'])
# @login_requried
# def crtt():
#
#     if request.method == 'POST':
#         connection = get_db()
#         username = request.form['username']
#         email = request.form['email']
#         pas = request.form['pass']
#         connection.execute('INSERT INTO users (username , email , pass) VALUES (?,?,?)',(username,generate_password_hash(email),pas))
#         connection.commit()
#         connection.close()
#         return redirect(url_for('index'))
#     return render_template('crt.html')

@app.route('/register', methods=['GET','POST'])

def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pas = request.form['pass']
        error = None

        if not username:
            error = "اسم المستخدم مطلوب"
        if not email:
            error = "الايميل  مطلوب"
        if not pas:
            error = "كلمة المرور مطلوبة"

        if error == None:
            connection = get_db()
            try:
                connection.execute('INSERT INTO users (username , email , pass) VALUES (?,?,?)',(username,email,generate_password_hash(pas),))
                connection.commit()
                connection.close()
            except connection.IntegrityError:
                error = f' مسجل بالفعل {username}'
            else:
                return redirect(url_for('login'))
            flash(error)

    return  render_template('auth/register.html')

@app.before_request
def load_logged_in_user():
    user_id = session.get('id')
    if user_id == None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()

@app.route('/logout')
def logout():
    session.clear()
    return  redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
