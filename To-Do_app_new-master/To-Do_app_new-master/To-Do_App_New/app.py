from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:psql@localhost/facebook'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    task_id=db.Column(db.Integer,primary_key=True, autoincrement=False)
    name=db.Column(db.String(100))
    done=db.Column(db.Boolean)

@app.route('/')
def home():
    todo_list=Todo.query.all()
    return render_template('home.html',todo_list=todo_list)

@app.route('/add' , methods=['POST'])
def add():
    name = request.form.get("name")
    existing_task = Todo.query.filter_by(name=name).first()
    
    if existing_task:
        return "Task with this name already exists!"
    last_task = Todo.query.order_by(Todo.task_id.desc()).first()

    if last_task:
        new_task_id = last_task.task_id + 1
    else:
        new_task_id = 1
    new_task = Todo(task_id=new_task_id, name=name, done=False)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
def update(todo_id):
    todo = Todo.query.get(todo_id)

    if request.method == 'POST':
        updated_name = request.form.get("updated_name")
        todo.name = updated_name
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('update.html', todo=todo)


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo= Todo.query.get(todo_id)
    db.session.delete(todo)
    tasks_to_update = Todo.query.filter(Todo.task_id > todo_id).all()
    for task in tasks_to_update:
        task.task_id -= 1
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)