import csv
import os
from abc import ABC, abstractmethod
from datetime import datetime

class IInputSource(ABC):
    @abstractmethod
    def get_assignments(self):
        pass

class IStorage(ABC):
    @abstractmethod
    def save(self, assignments):
        pass

    @abstractmethod
    def load(self):
        pass

class Assignment:
    _id_counter = 1

    def __init__(self, name, subject, due_date_str, due_time_str="23:59", id=None):
        if id:
            self._id = id
            Assignment._id_counter = max(Assignment._id_counter, id + 1)
        else:
            self._id = Assignment._id_counter
            Assignment._id_counter += 1

        self._name = ""
        self._subject = ""
        self._due_datetime = None

        self.name = name
        self.subject = subject
        self.set_deadline(due_date_str, due_time_str)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not value.strip(): raise ValueError("Name empty")
        self._name = value.strip()

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = value.strip() if value else "General"

    def set_deadline(self, date_str, time_str):
        try:
            if not time_str: time_str = "23:59"
            self._due_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Bad Date Format")

    def get_time_remaining(self):
        return self._due_datetime - datetime.now()

    def to_dict(self):
        delta = self.get_time_remaining()
        total_seconds = delta.total_seconds()

        if total_seconds < 0:
            status, urgency = "Overdue", 4
        elif total_seconds < 3600:
            status, urgency = "Due Soon!", 3
        elif total_seconds < 86400:
            status, urgency = "Today", 2
        elif total_seconds < 259200:
            status, urgency = "Upcoming", 1
        else:
            status, urgency = "Planned", 0

        if total_seconds < 0:
            time_text = f"{int(abs(total_seconds) / 3600)}h ago"
        elif total_seconds < 86400:
            time_text = f"{int(total_seconds // 3600)}h {int((total_seconds % 3600) // 60)}m left"
        else:
            time_text = f"{int(total_seconds // 86400)} days left"

        return {
            "id": self._id, "name": self._name, "subject": self._subject,
            "due_date": self._due_datetime.strftime("%Y-%m-%d"),
            "due_time": self._due_datetime.strftime("%I:%M %p"),
            "time_text": time_text, "status": status, "urgency": urgency
        }

class ManualInputSource(IInputSource):
    def __init__(self, form_data):
        self._form_data = form_data

    def get_assignments(self):
        try:
            return [Assignment(
                self._form_data.get('name'),
                self._form_data.get('subject'),
                self._form_data.get('due_date'),
                self._form_data.get('due_time')
            )]
        except ValueError:
            return []

class CsvStorage(IStorage):
    def __init__(self, filename='schedule.csv'):
        self._filename = filename

    def load(self):
        items = []
        if not os.path.exists(self._filename):
            return items

        try:
            with open(self._filename, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        items.append(Assignment(
                            name=row['name'], subject=row['subject'],
                            due_date_str=row['due_date'], due_time_str=row['due_time'],
                            id=int(row['id'])
                        ))
                    except (ValueError, KeyError):
                        continue  # Skip bad rows
        except Exception as e:
            print(f"Error reading CSV: {e}")
        return items

    def save(self, assignments):
        try:
            with open(self._filename, mode='w', newline='', encoding='utf-8') as f:
                fieldnames = ['id', 'name', 'subject', 'due_date', 'due_time']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in assignments:
                    writer.writerow({
                        'id': item.id, 'name': item.name, 'subject': item.subject,
                        'due_date': item._due_datetime.strftime("%Y-%m-%d"),
                        'due_time': item._due_datetime.strftime("%H:%M")
                    })
        except Exception as e:
            print(f"Error saving CSV: {e}")

class ScheduleManager:
    def __init__(self, storage: IStorage):
        self._storage = storage
        self._assignments = []
        self._reload_data()

    def _reload_data(self):
        self._assignments = self._storage.load()

    def add_assignment(self, source: IInputSource):
        new_items = source.get_assignments()
        self._assignments.extend(new_items)
        self._storage.save(self._assignments)

    def discard_assignment(self, assignment_id):
        self._assignments = [a for a in self._assignments if a.id != assignment_id]
        self._storage.save(self._assignments)

    def process_and_sort(self):
        processed_list = [a.to_dict() for a in self._assignments]
        processed_list.sort(key=lambda x: x['urgency'], reverse=True)
        return processed_list
