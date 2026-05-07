[![CI](https://github.com/Calloumi05/Smart-Task-Manager/actions/workflows/python-app.yml/badge.svg)](https://github.com/Calloumi05/Smart-Task-Manager/actions/workflows/python-app.yml)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

# Smart-Task-Manager
A desktop application that helps university students manage their academic workload with deadline tracking, task organisation, and visual urgency indicators.

# Overview

University students struggle to manage multiple assignments, lab reports, and project deadlines simultaneously. Smart-Task addresses this pain point by providing a centralised, visual task management system that goes beyond a simple to-do list. The application helps students prioritise work by showing upcoming deadlines with colour-coded urgency indicators and providing a clear dashboard of their academic workload.

# Features
- **Dark Mode** - Toggle between light and dark colour schemes for comfortable viewing in any lighting condition.
- **Subject Sorter** - Organise and filter tasks by academic subject (Maths, English, History, etc.) to focus on specific courses.
- **Delete Tasks** - Remove unwanted tasks with confirmation to prevent accidental deletion.
- **Countdown** - Visual countdown timer showing days and hours remaining until each task deadline.
- **Completed Task Congratulations** - Confetti celebration animation and success message when you mark a task as complete.
- **Mini Game for Trashing Items** - Play a Flappy Bird-style game (Flappy Book) to confirm task deletion - score 5 points to permanently trash the task.
- **Pomodoro Timer** - Built-in study timer using the Pomodoro Technique (25 minutes work, 5 minutes break) to boost productivity.
- **Calendar View** - Visual calendar interface showing all tasks organised by due date for better workload planning.

# Getting Started
#### Option: Direct Download 
1. Download the `student_task_tracker.py` file from the repository
2. Save it to a folder on your computer
3. Make sure the file has a `.py` extension

# Prerequisites
Python 3.8 or higher installed on your system
Git (for cloning the repository)

# Installation
No external dependencies required. The app uses only Python standard library:
- tkinter (built-in GUI framework)
- json (built-in data storage)
- datetime (built-in date handling)
- os (built-in file management)

# Running the App
Run `student_task_tracker.py` file in V7 folder to run the program

# Project Structure

```
Smart-Task-Manager/
│
├── .github/ # GitHub Actions CI/CD workflows
│   └── workflows/
│       └── tests.yml # Automated testing with pytest-cov
│
├── .vscode/ # VS Code workspace settings (team-wide config)
│
├── V7/ # MAIN WORKING VERSION - Latest stable release
│   ├── student_task_tracker.py # Core application code with all features
│   ├── test_student_task_tracker.py # Unit tests for the main application
│   ├── student_tasks.json # Active tasks data storage
│   └── deleted_tasks.json # Soft-deleted tasks storage
│
├── Old Versions/ # Archive of previous version prototypes
│   ├── Version 2/ # Early prototype (basic functionality)
│   ├── Version 3.1/ # First working base
│   ├── Version 3.2/ # Date validation fixes
│   ├── Version 3.3/ # Fully working base version
│   ├── Version 4/ # Split into branches (experimental)
│   ├── Version 5/ # Failed branch attempt
│   └── Version 6/ # Failed branch attempt
│
├── backups/ # Safety backups of working code
│
├── README.md # Project documentation
│
└── requirements.txt # Python dependencies (empty - uses only standard library)

```

# Architecture
We used a single StudentTaskTracker class (OOP) to manage state across methods without global variables. The code follows MVC: 
- Model: self.tasks, self.deleted_tasks, load_data(), save_data(), get_countdown() 
- View: create_gui(), populate_task_list(), apply_theme() 
- Controller: add_task(), delete_task(), toggle_done(), sort_*(), view_trash() 

Why JSON instead of CSV/SQLite: JSON handles nested task objects naturally, is human-readable, and uses Python's built-in json module. CSV lacks boolean support; SQLite adds unnecessary complexity for ~200 tasks. 

# Testing Summary

This project includes an automated testing file called `test_student_task_tracker.py`. It contains both unit tests and integration tests for the Student Task Tracker application.

The tests are written using Python’s built-in `unittest` module. They can also be run with `pytest` if it is installed, but no external testing library is required for the main test logic.

The test file is kept separate from the main application file, `student_task_tracker.py`, which is good practice because it allows the program logic to be tested without running the full Tkinter interface.

## How the Tests Avoid Opening the GUI

The Student Task Tracker is a Tkinter application, so normally importing or creating the app could open a window. The test file prevents this by using `unittest.mock.patch` to patch `tkinter.Tk`.

This means the tests can check the application’s logic without displaying the GUI.

## Example from the test file:

What the Tests Cover
The testing file checks several important parts of the planner.

Example Task Generation
The tests check that generate_example_tasks():

- creates the correct number of example tasks
- gives every task the required fields
- creates unique task IDs
- uses valid priority values
- stores the done field as a Boolean
- creates due dates in the correct DD/MM/YYYY HH:MM format
- Countdown Logic
- The tests check that get_countdown():

- returns a countdown for future dates
- returns "OVERDUE" for past dates
- returns "Invalid" for malformed dates
- handles tasks due later on the same day correctly

## Data Persistence
The tests check that save_data() and load_data():

- save tasks to JSON files
- reload saved tasks correctly
- handle empty task lists
- do not crash if files are missing
- preserve custom subjects after saving and loading

Temporary JSON files are used during these tests so the real application data is not damaged.

## Filter Logic
The tests check the _get_filtered_tasks() logic for:

- total tasks
- pending tasks
- completed tasks
- overdue tasks
- tasks due soon
- unknown filters

This confirms that dashboard-style filters return the correct subset of tasks.

## Sort Logic
The tests check that task data can be sorted by:

- ID
- title
- priority
- due date
- descending order

## Date Validation Logic
The tests include checks for date-related behaviour, including:

- detecting past dates
- allowing dates within a reasonable future range
- detecting dates more than one year away
- producing human-readable “ago” strings for old dates

## Task CRUD Logic
The tests cover basic task operations:

- creating a new task ID
- editing a task in place
- moving a task to trash
- restoring a task from trash
- toggling a task between done and not done

## Integration Tests

The integration tests check larger workflows, including:

- creating a task, saving it, and reloading it
- deleting a task to trash and restoring it
- combining overdue filtering with search logic
- sorting multiple tasks by deadline
- confirming saved JSON files are valid and readable

## Changes or Requirements in student_task_tracker.py
For this test file to work, the main script must be saved as:

student_task_tracker.py

The main script must include the following functions, classes, or methods:

- generate_example_tasks()
- EXAMPLE_TASK_TEMPLATES
- StudentTaskTracker
- StudentTaskTracker.get_countdown()
- StudentTaskTracker.save_data()
- StudentTaskTracker.load_data()
- StudentTaskTracker._get_filtered_tasks()

The _get_filtered_tasks() method is especially important because several tests depend on it. If this method is not present in the main program, the filter tests will fail.

The get_countdown() method should also handle invalid dates safely by returning "Invalid" rather than crashing.

## How to Run the Tests
Make sure both files are in the same folder:

- student_task_tracker.py
- test_student_task_tracker.py

To run using Python’s built-in unittest system:

- python test_student_task_tracker.py

Or:

- python -m unittest -v test_student_task_tracker.py

If pytest is installed, the tests can also be run with:

- python -m pytest test_student_task_tracker.py -v

   - ## Expected Test Output
A successful run should show each test name followed by ok, then a final summary similar to:

Ran 45 tests in 0.10s

OK
This means all unit and integration tests passed successfully.

Note About the Terminal Closing
If the test file is double-clicked, the terminal may close immediately after the tests finish. To avoid this, run the tests from an already-open terminal using:

python test_student_task_tracker.py
This keeps the terminal open so the results can be read.

<img width="1060" height="247" alt="image" src="https://github.com/user-attachments/assets/8bb4dcf2-0609-47d4-9d2c-56977e945c4a" />



# Known Issues
- Dark Mode is not always consistent
- Pomodoro timer can get stuck on times

# Contributing
We used this branching strategy:
- Main Branch - has the main working base code
- New Feature Branches - (e.g., feature/trash-bin, feature/dark-mode) are after merged to Main Branch once tested

### Workflow:
1. Create a branch from main
2. Make changes and test locally
3. Commit with descriptive messages
4. Push to GitHub
5. Open a Pull Request on GitHub
6. After review, merge to main


# Design Decisions Log
- 05/05/26 We used branches eg. V7-Bin to develop and test new features without breaking the working V7-Base code. This allowed us to safely experiement and only merge features when they were working and complete.
- 06/05/26 We added comprehensive docstrings to all code to improve code readability for team collaboration and helps future developers (including ourselves) understand the purpose of each component.
   
# Team
 
| Team Member | GitHub | Contributions |
|---|---|---|
| Callum | [@Calloumi05](https://github.com/Calloumi05) | Created the core V7 base application, dark mode, sorting functionality, data persistence, Genral improvment , README documentation |
| Tania | [@Tania881](https://github.com/Tania881) | Bin game (FlappyBook), docstrings, CI pipeline and badges, README documentation, UI touch-ups |
| Phoebe | [@phoebe477](https://github.com/phoebe477) | Calendar view, large countdown clock, Pomodoro timer, UI improvements, celebration message, README documentation |
| Ollie | [@KaratePigeon](https://github.com/KaratePigeon) | Test suite, example test dataset, file organisation, sorting feature, repository tidying, README documentation |
| Lilith | [@lilith985](https://github.com/lilith985) | README documentation, |

# Changelog


### Version 2 notes 
Version 2 was a good test code to see rough ideas of how to create a student task manager but needs some work on

### Version 3 and 3.1 notes 
Version 3 and 3.1 is a good working base to work upon. 
Work to be done on version 3: 
- update the dark mode feature so it works on the whole screen 
- run tests to check all features work and no incorrect dates ccan be added 
- clean up code so easier to follow 
- make sure if you multiselect the feature you want to perform is applied to all and not just one of the tasks 

### Version 3.2 has been created:
### Version 3.2 notes and update:
Version 3.2 has been created to solve the date issue and now provides hints to ht euser when it detects an issue with the date entered
issues still with:
- dark mode was semi fixed but still needs work upon 
- and the multiselect still needs fixing (was not focused on in the fix of version 3.1)

### Version 3.3 has all correction made

# Version 3.3 interface

<img width="1390" height="887" alt="Screenshot 2026-05-04 161305" src="https://github.com/user-attachments/assets/8857237b-d2ff-407d-8bf0-a3c0d8773128" />

### Version 4 been split into branches like coursework wanted 
Work on the seperate branched and then import them into the main version 4 
currently needs alot of work 

### Version 5 nor 6 work (failed attempts)
trying to discover how to use branches but no success watched videos to learn and version 7 is where progress will continue 

### Version 7 has been created 
Version 7 works successfully. Branches will now be used to improve feature of this such as task, gui, and so on. 
Below is a snap shot of first rendition of version 7's interface. 

<img width="1918" height="991" alt="image" src="https://github.com/user-attachments/assets/06d77878-bda3-4b32-a99a-bcb3deb4c97a" />


### Version 7 has been created  
This version works perfectly adn we now aim to work in branches to develop features of it to then merge back in 

### Version 7 improvements 
- add congratulations message when a task is marked as done
- darkmode improved
- large countdown clock
- bin view to drag tasks to
- Mini Game for Trashing Items
- make it so user can select multiple taks to bin
- show upcoming tasks on a calendar view
- larger clearer dashboard showing tasks to do, and next latest task
- colour for priority of tasks (coloured for deadline proximity)
- add tests for dates, correct spelling of subjects, etc
- add a feature so when you click headings at the top of the table it will sort it by title, date, priority and so on
  
  # Version 7 completed impovements
  - bin has been made
    <img width="1907" height="962" alt="image" src="https://github.com/user-attachments/assets/db82010d-ad42-4b1b-911b-f8d5cecc52b3" />
    
  - large countdown clock has been added
    <img width="1730" height="817" alt="image" src="https://github.com/user-attachments/assets/bc5bbf98-41ca-40a4-826f-0af36ada7260" />
    
  - example data has been added for purposes for testing and celebration message feature added when task is marked as done
  - <img width="1907" height="1010" alt="image" src="https://github.com/user-attachments/assets/5c0c407f-20b8-4f6d-a08a-66a5c8256cce" />

  - dark mode fixed to cover full screen
  - <img width="1918" height="986" alt="image" src="https://github.com/user-attachments/assets/411072e3-4d31-4a21-858d-b9793e029eee" />
  
  - code includes doc strings for easier readability
  - <img width="860" height="672" alt="image" src="https://github.com/user-attachments/assets/6612c53d-4c8c-47c5-b82c-60ea9884cdb9" />
  
  - Calendar view has been added so students can track tasks more easily
  - <img width="1882" height="996" alt="image" src="https://github.com/user-attachments/assets/c6423376-9886-4e19-b178-157dc141d0b2" />
  
  - Search bar now filters in real time as you type, no need to click the search button
    
  - Search now covers both task title and subject, so you can filter by subject name directly
    
  - Removed the Sort Deadline and Sort Priority buttons to reduce clutter
    
  - Clicking any column heading (Title, Subject, Priority, Due, Countdown, Status) now sorts the list by that column, click the same heading again to reverse the order
  
  - A ▲/▼ arrow appears on the active column so you always know how the list is sorted
  - <img width="3795" height="1962" alt="image" src="https://github.com/user-attachments/assets/86bf10f7-846d-441b-ac6d-5cad64de202c" />

  - updated interface to sort by colour further and make the interface alot more modern
  - <img width="1917" height="987" alt="image" src="https://github.com/user-attachments/assets/4930155b-5a48-4b38-a09a-11a361192cfd" />

  - Sort by header feature re added back in
  - <img width="1872" height="860" alt="image" src="https://github.com/user-attachments/assets/c08f8d4a-2324-455f-8730-3c1cb0c16d0d" />

  - Final features were added including a pomodoro timer and making sure all the code was nicely formatted
  - <img width="1917" height="1015" alt="image" src="https://github.com/user-attachments/assets/78de4bfb-d4a0-4f11-aa08-9a97267d360b" />

  - ## Testing Summary

This project includes an automated testing file called `test_student_task_tracker.py`. It contains both unit tests and integration tests for the Student Task Tracker application.

The tests are written using Python’s built-in `unittest` module. They can also be run with `pytest` if it is installed, but no external testing library is required for the main test logic.

The test file is kept separate from the main application file, `student_task_tracker.py`, which is good practice because it allows the program logic to be tested without running the full Tkinter interface.

## How the Tests Avoid Opening the GUI

The Student Task Tracker is a Tkinter application, so normally importing or creating the app could open a window. The test file prevents this by using `unittest.mock.patch` to patch `tkinter.Tk`.

This means the tests can check the application’s logic without displaying the GUI.

Example from the test file:

What the Tests Cover
The testing file checks several important parts of the planner.

Example Task Generation
The tests check that generate_example_tasks():

creates the correct number of example tasks
gives every task the required fields
creates unique task IDs
uses valid priority values
stores the done field as a Boolean
creates due dates in the correct DD/MM/YYYY HH:MM format
Countdown Logic
The tests check that get_countdown():

returns a countdown for future dates
returns "OVERDUE" for past dates
returns "Invalid" for malformed dates
handles tasks due later on the same day correctly
Data Persistence
The tests check that save_data() and load_data():

save tasks to JSON files
reload saved tasks correctly
handle empty task lists
do not crash if files are missing
preserve custom subjects after saving and loading
Temporary JSON files are used during these tests so the real application data is not damaged.

Filter Logic
The tests check the _get_filtered_tasks() logic for:

total tasks
pending tasks
completed tasks
overdue tasks
tasks due soon
unknown filters
This confirms that dashboard-style filters return the correct subset of tasks.

Sort Logic
The tests check that task data can be sorted by:

ID
title
priority
due date
descending order
Date Validation Logic
The tests include checks for date-related behaviour, including:

detecting past dates
allowing dates within a reasonable future range
detecting dates more than one year away
producing human-readable “ago” strings for old dates
Task CRUD Logic
The tests cover basic task operations:

creating a new task ID
editing a task in place
moving a task to trash
restoring a task from trash
toggling a task between done and not done
Integration Tests
The integration tests check larger workflows, including:

creating a task, saving it, and reloading it
deleting a task to trash and restoring it
combining overdue filtering with search logic
sorting multiple tasks by deadline
confirming saved JSON files are valid and readable
Changes or Requirements in student_task_tracker.py
For this test file to work, the main script must be saved as:

student_task_tracker.py
The main script must include the following functions, classes, or methods:

generate_example_tasks()
EXAMPLE_TASK_TEMPLATES
StudentTaskTracker
StudentTaskTracker.get_countdown()
StudentTaskTracker.save_data()
StudentTaskTracker.load_data()
StudentTaskTracker._get_filtered_tasks()
The _get_filtered_tasks() method is especially important because several tests depend on it. If this method is not present in the main program, the filter tests will fail.

The get_countdown() method should also handle invalid dates safely by returning "Invalid" rather than crashing.

How to Run the Tests
Make sure both files are in the same folder:

student_task_tracker.py
test_student_task_tracker.py
To run using Python’s built-in unittest system:

python test_student_task_tracker.py
Or:

python -m unittest -v test_student_task_tracker.py
If pytest is installed, the tests can also be run with:

python -m pytest test_student_task_tracker.py -v
Expected Test Output
A successful run should show each test name followed by ok, then a final summary similar to:

Ran 45 tests in 0.10s

OK
This means all unit and integration tests passed successfully.

Note About the Terminal Closing
If the test file is double-clicked, the terminal may close immediately after the tests finish. To avoid this, run the tests from an already-open terminal using:

python test_student_task_tracker.py
This keeps the terminal open so the results can be read.

  - <img width="1060" height="247" alt="image" src="https://github.com/user-attachments/assets/8bb4dcf2-0609-47d4-9d2c-56977e945c4a" />




  
