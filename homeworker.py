""" homeworker - Ryan Cotsakis """

import os
import sys
import time
import threading

listenerDied = False
commands = []
currentTasks = []
completedTasks = []

DELAY = 0.1 #seconds per cycle (2*DELAY < WAIT)
WAIT = 0.2 #seconds for >>
CURRENTHEADER = "CURRENT TASKS:"
COMPLETEDHEADER = "COMPLETED TASKS:"
CLEAR_COMMAND = "cls"

def listener():
	while True:
		command = raw_input("\n>> ").strip()
		commands.append(command)
		if command in "exit" and command[0] == "e":
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
	print "done\t\t-logs the current task as complete"
	print "exit\t\t-close program"
	print "log\t\t-view the log of completed tasks"
	print "switch\t\t-switch to a different task"

	print "\nThe number after each task corresponds to the number\nof minutes it has been actively worked on"
	print "\nYour current tasks are:"
	print '\n'.join(currentTasks)

	p = threading.Thread(target = listener)
	p.start()
	cycleCount = 0
	while True:
		cycleCount += 1
		sys.stdout.flush()

		if listenerDied:
			data = update(f)
			break

		if not cycleCount % (60/DELAY):
			if len(currentTasks):
				currentTask = currentTasks[0].split('\t')
				currentTaskDuration = int(currentTask[1])
				currentTasks[0] = currentTask[0] + '\t' + str(currentTaskDuration+1)
			data = update(f)


		if len(commands):
			command = commands[0]
			del commands[0]
			if command in "log" and command[0] == "l":
				print '\n'.join(data)

			elif command in "exit" and command[0] == "e":
				data = update(f)
				break

			elif command in "add" and command[0] == "a":
				print "Enter New Line:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				newLine = commands[0] + "\t0"
				del commands[0]
				currentTasks.append(newLine)
				data = update(f)
				print "Task added!"

			elif command in "current" and command[:2] == "cu":
				print "Your current tasks are:"
				print '\n'.join(currentTasks)

			elif command in "done" and command[0] == "d":
				try:
					finishedTask = currentTasks[0]
					del currentTasks[0]
					completedTasks.append(finishedTask)
					data = update(f)
					print "Well done!"
				except IndexError:
					print "Done what?"

			elif command in "clear" and command[:2] == "cl":
				os.system(CLEAR_COMMAND)

			elif command in "switch" and command[0] == "s":
				itemNum = 0
				for item in currentTasks:
					print str(itemNum) + ": " + item
					itemNum += 1
				print "\nType the number corresponding to the task you'd like\nto switch to:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				try:
					itemNum = int(commands[0])
					currentTask = currentTasks[itemNum]
					del currentTasks[itemNum]
					currentTasks.insert(0,currentTask)
					data = update(f)
					print "Successfully switched to task " + str(itemNum)
					del commands[0]
				except (ValueError, IndexError):
					print "Could not switch to task '" + commands[0] + "'"

			elif command in "continue" and command[:2] == "co":
				itemNum = 0
				for item in completedTasks:
					print str(itemNum) + ": " + item
					itemNum += 1
				print "\nType the number corresponding to the task you'd like\nto continue:"
				sys.stdout.flush()
				while not len(commands):
					time.sleep(DELAY)
					sys.stdout.flush()
				try:
					itemNum = int(commands[0])
					currentTask = completedTasks[itemNum]
					del completedTasks[itemNum]
					currentTasks.insert(0,currentTask)
					data = update(f)
					print "Successfully switched to task " + str(itemNum)
					del commands[0]
				except (ValueError, IndexError):
					print "Could not switch to task '" + commands[0] + "'"

			else:
				print "Invalid command, " + command

		time.sleep(DELAY)
		# End of while(True)

	try:
		f.close()
	except:
		pass

if __name__ == '__main__':
	main()