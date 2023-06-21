# required modules for application development::::::::::::
from flask import Flask, render_template, redirect, url_for, request, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

# intialization of Flask webApp::::::::::::
app = Flask(__name__)
app.secret_key = "I Know your weekness"

# mongodb database uri for connection::::::::::::: 
DATABASE_URI = 'mongodb://127.0.0.1:27017/ToDo_App'
app.config['MONGO_URI'] = DATABASE_URI
# intitialize driver for database CRUD operations::::::::::
database = PyMongo(app)


# first route or entring point of WebApplication::::::::::::
@app.route('/')
def index():
    # this will redirecting to signin page
    return redirect('signin') 


# user sign in route, this will render signin page::::::::::::
@app.route('/signin', methods=['GET','POST'])
def signin():
    # when user start entering credentials into signin form
    if request.method == 'POST':
        # extracting data from signin form for authentication
        email = request.form['email']
        password = request.form['password']
        
        # checking database, if user present with entered mail address or not
        user_present = database.db.user_credentials.find_one({'email':email})
        
        # if user present and user entered correct password then user will redirecting to their dashboard page 
        if user_present and check_password_hash(user_present['password'], password):
            # adding user into session
            session['user_email'] = email
            return redirect(url_for('todo_dashboard'))
        # if not user will get an error message "Entered any one of entry wrong..." on display
        else:
            return render_template('signin.html', flag=True)

    # first signin route, routing to signin page
    return render_template('signin.html', flag=False)


# user sign up route, this will render signup page:::::::::::::
@app.route('/signup', methods=['GET','POST'])
def signup():
    # when user start entering data into signup form
    if request.method == 'POST':
        # extracting data from signup form for new user registration
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # checking database, if anyone already present with entered mail address or not
        user_present = database.db.user_credentials.find_one({'email':email})
        if user_present:
            # if anyone presents then user will get an message "someone already present with this mail address! Try with another..." on display
            return render_template('signup.html', flag=True)
        else:
            # if not, then registering a new user into the database 
            new_user = {'name':name, 'email': email, 'password': password}
            result = database.db.user_credentials.insert_one(new_user)
            if result.inserted_id:
                print('Data inserted successfully!')
            else:
                print('Failed to insert data.')
            return render_template('signup.html')
    
    # first signup route, routing to signup page
    return render_template('signup.html', flag=False)


# route for logout, this will remove user from session and redirect to login page
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('signin'))


# route for CREATE operation, creating or adding new tasks::::::::::::
@app.route('/api/todo/add', methods=['GET','POST'])
def add_task():
    # taking email and task from todo_dashboard route
    email = session.get('user_email')
    task = request.args.get('task')

    # if user already have tasks, then we need to updates the tasks by adding new task
    if database.db.user_tasks.find_one({'email':email}):
        user = database.db.user_tasks.find_one({'email':email})
        # user_id for adding new task into that user task database
        user_id = user['_id']
        result = database.db.user_tasks.update_one({'_id':user_id},{"$push":{'tasks':task}})
        # after updating this code line redirects the route back to the dashboard
        return redirect(url_for('todo_dashboard'))
    # if user not have any tasks assigned, then create a new one
    else:
        task = {
            "email":email,
            "tasks":[task]
        }
        result = database.db.user_tasks.insert_one(task)
    
        # after creating this code line redirects the route back to the dashboard
        return redirect(url_for('todo_dashboard'))
    

# view function for deleting tasks and after deleting tasks, will redirect to dashboard
@app.route('/delete', methods=['GET', 'POST'])
def delete_task():
    #extracting email from session 
    email = session.get('user_email')
    task = request.form['task']

    # extracting user_id for deleting task from database
    user = database.db.user_tasks.find_one({'email':email})
    user_id = user['_id']

    #updating the database by deleting task from it.
    result = database.db.user_tasks.update_one({'_id':user_id},{"$pull":{'tasks':task}})

    # redirecting to dashboard
    return redirect(url_for('todo_dashboard'))


# route for user dashboard, this will render the dashboard page:::::::::::
@app.route('/api/todo', methods=['GET', 'POST'])
def todo_dashboard():
    # taking email from signin route for displaying user data on dashboard
    email = session.get('user_email')
    
    # redirecting to add_task route when user makes new task 
    if request.method == 'POST':
        task = request.form['task']
        return redirect(url_for('add_task', task=task))
    
    # this code will show users task on dashboard if users have any tasks
    if database.db.user_tasks.find_one({'email': email}):
        data = database.db.user_tasks.find_one({'email': email})
        task = data['tasks']
        return render_template('todo_dashboard.html', email=email, tasks=task)
    
    # else this will show an message to the user dashboard if tasks are not available
    return render_template('todo_dashboard.html', email=email, todos=0)


if __name__ == '__main__':
    app.run()