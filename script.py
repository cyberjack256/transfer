import csv
import json
import os
import argparse
import argcomplete
from datetime import datetime, timedelta
import webbrowser

# Dynamic paths for configuration and log files
DOCUMENTS_PATH = os.path.expanduser("~/Documents")
CONFIG_FILE = os.path.join(DOCUMENTS_PATH, 'class_config.json')
LOG_FILE = os.path.join(DOCUMENTS_PATH, 'class_log.txt')

# Directory paths for the class rosters
BASE_DIR = '/Users/jturner/Library/CloudStorage/Box-Box/Services Training and Implementation Program/CrowdStrike University Course Materials/Class Rosters/2024'
CLASS_DIRS = {
    'LOG 200': f'{BASE_DIR}/LOG 200',
    'LOG 201': f'{BASE_DIR}/LOG 201',
    'LOG 202': f'{BASE_DIR}/LOG 202'
}

# Load or create configuration
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        'users': [],
        'checklist': [],
        'incomplete_users': [],
        'class_details': {
            'LOG 200': {
                'day1_url': '',
                'passphrase': '',
                'day2_url': '',
                'encounter_id': '',
            },
            'LOG 201': {
                'url': '',
                'passphrase': '',
                'encounter_id': '',
            },
            'LOG 202': {
                'url': '',
                'passphrase': '',
                'encounter_id': '',
            }
        },
        'graphql_url': ''
    }

def log_action(action):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{datetime.now().isoformat()} - {action}\n")

def list_csv_files(class_name):
    dir_path = CLASS_DIRS[class_name]
    files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
    return files

def read_csv(file_path, class_name):
    users = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = {
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'email': row['Email'],
                'company': row['Company'],
                'class': class_name,
                'internal': row['Email'].endswith('@crowdstrike.com'),
                'complete': row['Completed'].lower() == 'yes',
                'present': False,
                'troubleshooting': '',
                'questions_asked': ''
            }
            users.append(user)
    return users

def write_csv(file_path, users):
    fieldnames = ['User Name', 'First Name', 'Last Name', 'Email', 'Company', 'Present', 'Completed']
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow({
                'User Name': user['email'],
                'First Name': user['first_name'],
                'Last Name': user['last_name'],
                'Email': user['email'],
                'Company': user['company'],
                'Present': 'Yes' if user['present'] else 'No',
                'Completed': 'yes' if user['complete'] else 'no'
            })

def check_previous_classes(email):
    previous_classes = [user['class'] for user in config['users'] if user['email'] == email]
    return previous_classes

def update_user_info():
    email = input("Enter user's email: ")
    user = next((u for u in config['users'] if u['email'] == email), None)
    if not user:
        print("User not found.")
        return
    
    user['location'] = input("Enter location: ")
    user['interests'] = input("Enter special interests: ")
    user['familiarity'] = input("Enter familiarity with product: ")
    user['feedback'] = input("Enter feedback: ")
    user['demographics'] = {
        'talkative': input("Was the user talkative? (yes/no): ").lower() == 'yes',
        'participative': input("Did the user participate? (yes/no): ").lower() == 'yes',
        'asked_questions': input("Did the user ask a lot of questions? (yes/no): ").lower() == 'yes',
        'irate': input("Was the user irate? (yes/no): ").lower() == 'yes',
    }
    user['complete'] = False
    config['incomplete_users'].append(email)
    log_action(f"Updated information for user {email}")

def add_troubleshooting_and_questions():
    email = input("Enter user's email: ")
    user = next((u for u in config['users'] if u['email'] == email), None)
    if not user:
        print("User not found.")
        return
    
    user['troubleshooting'] = input("Enter troubleshooting details: ")
    user['questions_asked'] = input("Enter questions asked: ")
    log_action(f"Added troubleshooting and questions for user {email}")

def generate_welcome_message(class_name, day=1):
    class_details = config['class_details'][class_name]
    
    if class_name == "LOG 200":
        message = f"""
Hello, and welcome{' back' if day == 2 else ''}! We will begin class shortly. While you’re waiting, please sign into CrowdStrike University:
[CrowdStrike University (CSU)](https://crowdstrike.litmos.com)

Helpful links:
[Falcon Encounter Login]({class_details['day1_url']})

Your Class Passphrase: {class_details['passphrase']}
Your Class Encounter ID: {class_details['encounter_id']}

Application link: [GitHub - cyberjack256/weather](https://github.com/cyberjack256/weather.git)

I’m looking forward to a great session!

Connect with/Contact Me:
LinkedIn: Cyberjack256
Email: mailto:Jack.Turner@crowdstrike.com
"""
    elif class_name == "LOG 201":
        message = f"""
Good morning/afternoon{'! Welcome back to Day 2 of Log 201' if day == 2 else ', and welcome!'}. While you’re waiting, please sign into CrowdStrike University:
[CrowdStrike University (CSU)](https://crowdstrike.litmos.com)

Sign into CloudShare: {class_details['url']}?passphrase={class_details['passphrase']}

I’m looking forward to a great session!

Connect with/Contact Me:
LinkedIn: https://www.linkedin.com/in/cyberjack256/
Email: mailto:jack.turner@crowdstrike.com
"""
    elif class_name == "LOG 202":
        message = f"""
Good morning/afternoon{'! Welcome back to Day 2 of Log 202' if day == 2 else ', and welcome!'}. While you’re waiting, please sign into CrowdStrike University:
[CrowdStrike University (CSU)](https://crowdstrike.litmos.com)

Sign into CloudShare: {class_details['url']}?passphrase={class_details['passphrase']}

I’m looking forward to a great session!

Connect with/Contact Me:
LinkedIn: https://www.linkedin.com/in/cyberjack256/
Email: mailto:jack.turner@crowdstrike.com
"""
    return message

def add_checklist_item(task):
    config['checklist'].append({'task': task, 'timestamp': datetime.now().isoformat()})
    log_action(f"Checklist item added: {task}")

def mark_users_complete():
    for user in config['users']:
        user['complete'] = True
    config['incomplete_users'] = []
    log_action("All users marked as complete.")

def remind_incomplete_users():
    if config['incomplete_users']:
        print("Reminder: The following users are not marked as complete:")
        for email in config['incomplete_users']:
            print(email)
        log_action("Reminder issued for incomplete users.")

def generate_tickcounter_url(start_time):
    class_start = start_time + timedelta(minutes=5)
    url = f"https://www.tickcounter.com/countdown/{class_start.year}{class_start.month:02}{class_start.day:02}/{class_start.hour:02}{class_start.minute:02}/{class_start.second:02}"
    return url

def display_menu():
    print("Menu:")
    print("1. Read CSV and update users")
    print("2. Check previous classes of a user")
    print("3. Update user information")
    print("4. Generate welcome message")
    print("5. Generate GraphQL queries")
    print("6. Add checklist item")
    print("7. Mark all users complete")
    print("8. Compare students across classes")
    print("9. Mark user present")
    print("10. Add troubleshooting and questions asked")
    print("11. Save and exit")

def compare_students():
    internal_users = [user for user in config['users'] if user['internal']]
    external_users = [user for user in config['users'] if not user['internal']]
    
    print("Internal Users:")
    for user in internal_users:
        print(f"{user['first_name']} {user['last_name']} - {user['email']} - Classes: {', '.join(check_previous_classes(user['email']))}")

    print("\nExternal Users:")
    for user in external_users:
        print(f"{user['first_name']} {user['last_name']} - {user['email']} - Classes: {', '.join(check_previous_classes(user['email']))}")

def mark_user_present():
    email = input("Enter user's email to mark as present: ")
    user = next((u for u in config['users'] if u['email'] == email), None)
    if user:
        user['present'] = True
        log_action(f"Marked user {email} as present")
    else:
        print("User not found.")

def main():
    remind_incomplete_users()
    
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            class_name = input("Enter class name (LOG 200, LOG 201, LOG 202): ")
            if class_name not in CLASS_DIRS:
                print("Invalid class name. Please try again.")
                continue
            csv_files = list_csv_files(class_name)
            if not csv_files:
                print("No CSV files found in the directory.")
                continue

            print("Select a CSV file:")
            for idx, file in enumerate(csv_files, 1):
                print(f"{idx}. {file}")
            file_choice = int(input("Enter the number of the CSV file to read: ")) - 1
            csv_file_path = os.path.join(CLASS_DIRS[class_name], csv_files[file_choice])
            users = read_csv(csv_file_path, class_name)
            config['users'].extend(users)
            log_action(f"Users read from CSV and updated for class {class_name}")
        elif choice == '2':
            email = input("Enter user's email to check previous classes: ")
            previous_classes = check_previous_classes(email)
            if previous_classes:
                print(f"User has attended previous classes: {', '.join(previous_classes)}")
            else:
                print("User has not attended any previous classes.")
            log_action(f"Checked previous classes for user {email}")
        elif choice == '3':
            update_user_info()
        elif choice == '4':
            class_name = input("Enter class name (LOG 200, LOG 201, LOG 202): ")
            day = int(input("Enter day (1 or 2): "))
            message = generate_welcome_message(class_name, day)
            print("Generated Welcome Message:\n", message)
            log_action(f"Welcome message generated for {class_name} day {day}")
        elif choice == '5':
            auth_token = input("Enter authorization token: ")
            encounter_id = input("Enter encounter ID: ")
            queries = generate_graphql_queries(auth_token, encounter_id)
            print("Generated GraphQL Queries:\n", queries)
            log_action("GraphQL queries generated")
        elif choice == '6':
            task = input("Enter checklist item: ")
            add_checklist_item(task)
        elif choice == '7':
            mark_users_complete()
        elif choice == '8':
            compare_students()
        elif choice == '9':
            mark_user_present()
        elif choice == '10':
            add_troubleshooting_and_questions()
        elif choice == '11':
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            for class_name, dir_path in CLASS_DIRS.items():
                csv_file_path = os.path.join(dir_path, 'roster.csv')
                write_csv(csv_file_path, [user for user in config['users'] if user['class'] == class_name])
            log_action("Configuration saved and exiting")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
