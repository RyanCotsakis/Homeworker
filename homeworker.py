""" homeworker - Ryan Cotsakis """

import win32gui, win32con
import os
import sys
import time
import threading
from datetime import date

listenerDied = False
paused = [False]
commands = []
currentTasks = []
completedTasks = []

DELAY = 0.1 #seconds per cycle (2*DELAY < WAIT)
WAIT = 0.2 #seconds for >>
CURRENTHEADER = "CURRENT TASKS:"
COMPLETEDHEADER = "COMPLETED TASKS:"
CLEAR_COMMAND = "cls"

def listener():
	time.sleep(WAIT)
	while True:
		if not paused[0]:
			command = raw_input("\n>> ").strip()
		else:
			command = raw_input("\nPAUSED >> ").strip()
		commands.append(command)
		if len(command) and command in "exit" and command[0] == "e":
			listenerDied = True
			return
		time.sleep(WAIT)

def update(file):
	data = [CURRENTHEADER]+currentTasks+[COMPLETEDHEADER]+completedTasks
	file.seek(0)
	file.write('\n'.join(data))
	file.truncate()
	return data

def main():
	try:
		f = open("./log.txt",mode = "r+")
		data = f.read().splitlines()
	except IOError:
		f = open("./log.txt",mode = "w")
		data = update(f)

	inCurrent = True
	for item in data:
		if (item != COMPLETEDHEADER and item != CURRENTHEADER and inCurrent):
			currentTasks.append(item)
		elif item == COMPLETEDHEADER:
			inCurrent = False
		elif not inCurrent:
			completedTasks.append(item)


	print "\nCOMMAND LIST:"
	print "add\t\t-add a task"
	print "clear\t\t-clear the output screen"
	print "continue\t-continue a completed task"
	print "current\t\t-display unfinished tasks"
	print "done\t\t-log the current task as complete"
	print "delete\t\t-delete an unfinished task"
	print "exit\t\t-close program"
	print "log\t\t-view the log of completed tasks"
	print "minimize\t-minimize homeworker"
	print "(un)pause\t-stop/start adding time to current task"
	print "switch\t\t-switch to a different task"

	print "\nThe time after each task corresponds to the amount\nof time it has been actively worked on.\n"
	commands.append('current')

	p = threading.Thread(target = listener)
	p.start()
	cycleCount = 0
	while True:
		if not paused[0]:
			cycleCount += 1

		if listenerDied:
			data = update(f)
			break

		if not cycleCount % (60/DELAY):
			if len(currentTasks):
				try:
					currentTask = currentTasks[0].split('\t')
					terms = len(currentTask)
					currentTaskHM = currentTask[terms-1].split(':')
					currentTaskM = int(currentTaskHM[1])
					currentTaskH = int(currentTaskHM[0])
					if currentTaskM < 59:
						currentTaskM += 1
					else:
						currentTaskM = 0
						currentTaskH += 1
					currentTasks[0] = '\t'.join(currentTask[:terms-1]) + '\t' + str(currentTaskH) + ':' + str(currentTaskM).zfill(2)
				except (ValueError, IndexError):
					pass
			data = update(f)


		if len(commands):
			command = commands[0]
			del commands[0]

			if not len(command):
				pass

			elif command in "log" and command[0] == "l":
				print '\n'.join(data)

			elif command in "exit" and command[0] == "e":
				data = update(f)
				break

			elif command in "minimize" and command[0] == "m" and not command[:3] == "miz":
				Minimize = win32gui.GetForegroundWindow()
				win32gui.ShowWindow(Minimize, win32con.SW_MINIMIZE)

			elif command in "unpaused" and (command[0] == "p" or command[0] == "u"):
				paused[0] = not paused[0]

			elif command in "add" and command[0] == "a":
				print "Enter New Line:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				if len(commands[0]):
					newLine = commands[0] + "\t0:00"
					del commands[0]
					currentTasks.append(newLine)
					data = update(f)
					print "Task added!"
				else:
					print "Task name must not be empty."

			elif command in "current" and command[:2] == "cu":
				if len(currentTasks):
					print "Your current tasks are:"
					print '\n'.join(currentTasks)
				else:
					print "You're all done!"

			elif command in "done" and command[:2] == "do":
				try:
					finishedTask = currentTasks[0]
					del currentTasks[0]
					completedTasks.append(date.today().strftime('%d.%m.%Y - ') + finishedTask)
					data = update(f)
					print "Well done!"
				except IndexError:
					print "Done what?"

			elif command in "delete" and command[:2] == "de":
				itemNum = 1
				for item in currentTasks:
					print str(itemNum) + ": " + item
					itemNum += 1
				print "\nType the number corresponding to the task you'd like\nto delete:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				try:
					itemNum = int(commands[0])-1
					del currentTasks[itemNum]
					data = update(f)
					print "Task Deleted."
					del commands[0]
				except (ValueError, IndexError):
					print "Could not delete task '" + commands[0] + "'"


			elif command in "clear" and command[:2] == "cl":
				os.system(CLEAR_COMMAND)

			elif command in "switch" and command[0] == "s":
				itemNum = 1
				for item in currentTasks:
					print str(itemNum) + ": " + item
					itemNum += 1
				print "\nType the number corresponding to the task you'd like\nto switch to:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				try:
					itemNum = int(commands[0])-1
					currentTask = currentTasks[itemNum]
					del currentTasks[itemNum]
					currentTasks.insert(0,currentTask)
					data = update(f)
					print "Successfully switched to task " + str(itemNum+1) + "."
					del commands[0]
				except (ValueError, IndexError):
					print "Could not switch to task '" + commands[0] + "'"

			elif command in "continue" and command[:2] == "co":
				itemNum = 1
				for item in completedTasks:
					print str(itemNum) + ": " + item
					itemNum += 1
				print "\nType the number corresponding to the task you'd like\nto continue:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				try:
					itemNum = int(commands[0])-1
					currentTask = completedTasks[itemNum]
					del completedTasks[itemNum]
					currentTasks.insert(0,currentTask)
					data = update(f)
					print "Successfully switched to task " + str(itemNum+1) + "."
					del commands[0]
				except (ValueError, IndexError):
					print "Could not continue task '" + commands[0] + "'."

			else:
				print "Invalid command, '" + command + "'."

		sys.stdout.flush()
		time.sleep(DELAY)
		# End of while(True)

	try:
		f.close()
	except:
		pass

if __name__ == '__main__':
	main()