""" homeworker - Ryan Cotsakis """

import win32gui
import win32con
import os
import sys
import time
import threading
from datetime import date

paused = False
listener_died = False
tracking_today = True

commands = []
current_tasks = []
completed_tasks = []
days = []

DELAY = 0.1  # seconds per cycle (2*DELAY < WAIT)
WAIT = 0.2  # seconds for >>

CURRENT_HEADER = "CURRENT TASKS:"
COMPLETED_HEADER = "COMPLETED TASKS:"
DAYS_HEADER = "TIME PER DAY:"
DAYS_SEPARATOR = " - "
DATE_FORMAT = '%d.%m.%Y'

CLEAR_COMMAND = "cls"
OPEN_COMMAND = "start notepad log.txt"


def listener():
    global listener_died
    time.sleep(WAIT)

    while True:
        if not paused and not tracking_today:
            command = raw_input("\n>> ").strip()
        elif paused and not tracking_today:
            command = raw_input("\n(P) >> ").strip()
        elif not paused and tracking_today:
            command = raw_input("\n(T) >> ").strip()
        elif paused and tracking_today:
            command = raw_input("\n(P,T) >> ").strip()

        commands.append(command)

        if len(command) and ((command in "exit" and command[0] == "e") or (command in "open" and command[0] == "o")):
            listener_died = True
            return

        time.sleep(WAIT)


def update(_file):
    data = [CURRENT_HEADER] + current_tasks + [COMPLETED_HEADER] + completed_tasks + [DAYS_HEADER] + days
    _file.seek(0)
    _file.write('\n'.join(data))
    _file.truncate()
    return data


def add_minute(time_string):
    try:
        time_string = time_string.split(':')
        time_string_m = int(time_string[1])
        time_string_h = int(time_string[0])
        if time_string_m < 59:
            time_string_m += 1
        else:
            time_string_m = 0
            time_string_h += 1
        return str(time_string_h) + ':' + str(time_string_m).zfill(2)
    except (ValueError, IndexError):
        return None


def main():
    global paused
    global tracking_today

    try:
        f = open("./log.txt", mode="r+")
        data = f.read().splitlines()
    except IOError:
        f = open("./log.txt", mode="w")
        data = update(f)

    stage = 0
    for item in data:
        if item == CURRENT_HEADER and stage == 0:
            stage += 1
        elif stage == 1:  # current tasks
            if item == COMPLETED_HEADER:
                stage += 1
            else:
                current_tasks.append(item)
        elif stage == 2:  # completed tasks
            if item == DAYS_HEADER:
                stage += 1
            else:
                completed_tasks.append(item)
        elif stage == 3:  # days
            days.append(item)

    commands.append('info')
    commands.append('current')

    p = threading.Thread(target=listener)
    p.start()

    cycle_count = 0
    while True:
        if not paused:
            cycle_count += 1

        if listener_died:
            break

        if not cycle_count % (60 / DELAY):
            if len(current_tasks):
                    current_task = current_tasks[0].split('\t')
                    current_tasks[0] = '\t'.join(current_task[:-1]) + '\t' + add_minute(current_task[-1])

            if tracking_today:
                today, today_index = None, None
                for i, day in enumerate(days):
                    day = day.split(DAYS_SEPARATOR)
                    if date.today().strftime(DATE_FORMAT) == day[0]:
                        today = day
                        today_index = i
                        break
                if today is not None:
                    today[1] = add_minute(today[1])
                    days[today_index] = DAYS_SEPARATOR.join(today)
                else:
                    days.append(date.today().strftime(DATE_FORMAT + DAYS_SEPARATOR) + "0:01")

            data = update(f)

        if len(commands):
            command = commands[0]
            del commands[0]

            if not len(command):
                pass

            elif command in "log" and command[0] == "l":
                print '\n'.join(data)

            elif command in "minimize" and command[0] == "m" and not command[:3] == "miz":
                minimize = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(minimize, win32con.SW_MINIMIZE)

            elif (command in "unpaused" and (command[0] == "p" or command[0] == "u")) or command == "P":
                paused = not paused

            elif command in "info" and command[0] == "i":
                print "\nCOMMAND LIST:"
                print "add(i)\t\t-add a task at index i"
                print "clear\t\t-clear the output screen"
                print "continue\t-continue a completed task"
                print "current\t\t-display unfinished tasks"
                print "done\t\t-log the current task as complete"
                print "delete\t\t-delete an unfinished task"
                print "exit\t\t-close program"
                print "info\t\t-repeat these instructions"
                print "log\t\t-view the log of completed tasks"
                print "minimize\t-minimize homeworker"
                print "open\t\t-close program, and open log.txt"
                print "(un)pause\t-stop/start adding time to current task (P)"
                print "today\t\t-toggle the option to track the day (T)"
                print "switch\t\t-switch to a different task"
                print "\nThe time after each task corresponds to the amount\nof time it has been actively worked on.\n"

            elif (command in "today" and command[0] == "t") or command == "T":
                tracking_today = not tracking_today

            elif (command in "add" and command[0] == "a") or command[:3] == "add":
                index = None
                if len(command) > 3:
                    try:
                        index = int(command[3:])
                        command = "..."  # Makes len(command) == 3
                    except ValueError:
                        print "Invalid command, '" + command + "'."
                if len(command) <= 3:
                    print "Enter New Line:"
                    sys.stdout.flush()
                    while not len(commands):
                        time.sleep(DELAY)
                        sys.stdout.flush()
                    if len(commands[0]) and not listener_died:
                        new_line = commands[0] + "\t0:00"
                        del commands[0]
                        if index is not None:
                            current_tasks.insert(index-1, new_line)
                        else:
                            current_tasks.append(new_line)
                        data = update(f)
                        print "Task added!"
                    elif not listener_died:
                        print "Task name must not be empty."

            elif command in "open" and command[0] == "o":
                f.close()
                time.sleep(DELAY)
                os.system(OPEN_COMMAND)
                return

            elif (command in "current" and command[:2] == "cu") or command == "ls":
                if tracking_today:
                    print days[-1]
                if len(current_tasks):
                    print "Your current tasks are:"
                    print '\n'.join(current_tasks)
                else:
                    print "You're all done!"

            elif command in "done" and command[:2] == "do":
                try:
                    finished_task = current_tasks[0]
                    del current_tasks[0]
                    completed_tasks.append(date.today().strftime(DATE_FORMAT + DAYS_SEPARATOR) + finished_task)
                    data = update(f)
                    print "Well done!"
                except IndexError:
                    print "Done what?"

            elif command in "delete" and command[:2] == "de":
                item_num = 1
                for item in current_tasks:
                    print str(item_num) + ": " + item
                    item_num += 1
                print "\nType the number corresponding to the task you'd like\nto delete:"
                sys.stdout.flush()
                while not len(commands):
                    time.sleep(DELAY)
                    sys.stdout.flush()
                try:
                    item_num = int(commands[0]) - 1
                    del current_tasks[item_num]
                    data = update(f)
                    print "Task Deleted."
                    del commands[0]
                except (ValueError, IndexError):
                    print "Could not delete task '" + commands[0] + "'"

            elif command in "clear" and command[:2] == "cl":
                os.system(CLEAR_COMMAND)

            elif (command in "switch" and command[0] == "s") or command == "cd":
                item_num = 1
                for item in current_tasks:
                    print str(item_num) + ": " + item
                    item_num += 1
                print "\nType the number corresponding to the task you'd like\nto switch to:"
                sys.stdout.flush()
                while not len(commands):
                    time.sleep(DELAY)
                    sys.stdout.flush()
                try:
                    item_num = int(commands[0]) - 1
                    current_task = current_tasks[item_num]
                    del current_tasks[item_num]
                    current_tasks.insert(0, current_task)
                    data = update(f)
                    print "Successfully switched to task " + str(item_num + 1) + "."
                    del commands[0]
                except (ValueError, IndexError):
                    print "Could not switch to task '" + commands[0] + "'"

            elif command in "continue" and command[:2] == "co":
                item_num = 1
                for item in completed_tasks:
                    print str(item_num) + ": " + item
                    item_num += 1
                print "\nType the number corresponding to the task you'd like\nto continue:"
                sys.stdout.flush()
                while not len(commands):
                    time.sleep(DELAY)
                    sys.stdout.flush()
                try:
                    item_num = int(commands[0]) - 1
                    current_task = completed_tasks[item_num]
                    del completed_tasks[item_num]
                    current_tasks.insert(0, current_task)
                    data = update(f)
                    print "Successfully switched to task " + str(item_num + 1) + "."
                    del commands[0]
                except (ValueError, IndexError):
                    print "Could not continue task '" + commands[0] + "'."

            else:
                print "Invalid command, '" + command + "'."

        sys.stdout.flush()
        time.sleep(DELAY)
    # End of while(True)

    f.close()


if __name__ == '__main__':
    main()
