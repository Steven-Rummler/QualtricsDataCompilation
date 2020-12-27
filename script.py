import csv
import glob
from io import TextIOWrapper
from zipfile import ZipFile
import datetime

files = glob.glob("*.zip")
print(len(files), "valid reports found.  Processing...")
session_files = {}

for file in files:
    with ZipFile(file) as zipfile:
        with zipfile.open(zipfile.namelist()[0]) as csvFile:
            csvReader = csv.reader(TextIOWrapper(csvFile, 'utf-8'))
            session_files[zipfile.namelist()[0]] = []
            for row in csvReader:
                session_files[zipfile.namelist()[0]].append(row)

class Session:
    def __init__(self, name):
        self.name = name
        self.rating_count = 0
        self.rating_sum = 0
        self.entries = []

    def get_row(self):
        return [self.name, self.rating_count, self.rating_sum / self.rating_count]

class Entry:
    def __init__(self, name, submitted, ontime, participate, others):
        self.name = name
        self.submitted = submitted
        self.ontime = ontime
        self.participate = participate
        self.others = others

    def to_string(self):
        return self.session + ":\n" + self.name + " " + self.ontime + " " + str(self.participate) + "\n" + ", ".join(self.others)


sessions = []

current_session = 0
for name, rows in session_files.items():
    sessions.append(Session(name))
    for row in rows:
        if (row[4] == "100"):
            if (row[17] != ""):
                sessions[current_session].entries.append(Entry(" ".join(row[17].split()), datetime.datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S'), row[18], int(
                    row[19][0]), " ".join(row[21].split()).split(",")))
                sessions[current_session].rating_count += 1
                sessions[current_session].rating_sum += int(row[22][0])
    current_session += 1


print("Files processed.", len(sessions), "sessions.")

print("Compiling data...")

class Student:
    def __init__(self, name):
        self.name = name
        self.total_count = 0
        self.late_count = 0
        self.participate_sum = 0
        self.nominations = 0

    def to_string(self):
        return self.name + " " + str(self.total_count) + " " + str(self.late_count) + " " + str(self.participate_sum) + " " + str(self.nominations)

    def get_row(self):
        return [self.name, self.total_count, self.late_count, self.participate_sum / self.total_count, self.nominations]


students = {}

for session in sessions:
    session_students = []
    for entry in reversed(session.entries):
        if entry.name not in session_students:
            session_students.append(entry.name)
            if entry.name != "":
                if entry.name not in students:
                    students[entry.name] = Student(entry.name)

                students[entry.name].total_count += 1
                if (entry.ontime == "No"):
                    students[entry.name].late_count += 1
                students[entry.name].participate_sum += entry.participate

for session in sessions:
    session_students = []
    for entry in reversed(session.entries):
        if entry.name not in session_students:
            session_students.append(entry.name)
            for other in entry.others:
                if other != "":
                    if other not in students:
                        print("Nomination for nonexistent student:", other)
                    else:
                        students[other].nominations += 1

print("Generating reports...")

student_header = ["Name", "# Submitted", "# Late", "Avg Rating", "Nominations"]
session_header = ["Name", "Count", "Avg Rating"]

student_data = []
session_data = []

for name, student in students.items():
    student_data.append(student.get_row())
for session in sessions:
    session_data.append(session.get_row())

with open("student_report.csv", "w", newline='') as student_report:
    writer = csv.writer(student_report)
    writer.writerow(student_header)
    writer.writerows(student_data)
with open("session_report.csv", "w", newline='') as session_report:
    writer = csv.writer(session_report)
    writer.writerow(session_header)
    writer.writerows(session_data)

print("Reports generated.")