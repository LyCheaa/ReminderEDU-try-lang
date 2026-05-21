from flask import Flask, render_template, request, redirect, url_for
from core_logic import ScheduleManager, ManualInputSource, CsvStorage

app = Flask(__name__)
storage = CsvStorage('schedule.csv')
manager = ScheduleManager(storage)
@app.route('/')
def index():
    assignments = manager.process_and_sort()
    return render_template('index.html', assignments=assignments)

@app.route('/add', methods=['POST'])
def add_schedule():
    form_data = request.form
    manual_source = ManualInputSource(form_data)

    try:
        manager.add_assignment(manual_source)
    except Exception as e:
        print(f"Error adding assignment: {e}")

    return redirect(url_for('index'))

@app.route('/discard/<int:assignment_id>', methods=['POST'])
def discard_schedule(assignment_id):
    try:
        manager.discard_assignment(assignment_id)
    except Exception as e:
        print(f"Error discarding: {e}")

    return redirect(url_for('index'))


if __name__ == '__main__':
    import os

    if not os.path.exists('schedule.csv'):
        with open('schedule.csv', 'w', newline='') as f:
            f.write("id,name,subject,due_date,due_time\n")

    app.run(debug=True)
