""" homeworker - Ryan Cotsakis """

import sys
import time
import threading

commands = []

REPRINT = 1 #minutes between reprint
DELAY = 0.1 #seconds per cycle
CURRENTHEADER = "CURRENT TASKS:"
COMPLETEDHEADER = "COMPLETED TASKS:"

def listener():
	while True:
		command = raw_input("\n>> ").strip()
		commands.append(command)
		if command in "exit" and command[0] == "e":
			return
		time.sleep(1)

def write_to_file(file,text):
	file.seek(0)
	file.write(text)
	file.truncate()

def main():
	try:
		f = open("./log.txt",mode = "r+")
		data = f.read().splitlines()
	except IOError:
		f = open("./log.txt",mode = "w")
		data = [CURRENTHEADER, COMPLETEDHEADER]
		write_to_file(f,"\n".join(data))

	currentTasks = []
	completedTasks = []
	inCurrent = True
	for item in data:
		if (item != COMPLETEDHEADER and item != CURRENTHEADER and inCurrent):
			currentTasks.append(item)
		elif item == COMPLETEDHEADER:
			inCurrent = False
		elif not inCurrent:
			completedTasks.append(item)


	print "\nCOMMAND LIST:"
	print "log\t\t-view the log of completed tasks"
	print "find\t\t-search for query in log"
	print "current\t\t-view current task"
	print "switch\t\t-switch to a different task"
	print "done\t\t-logs the current task as complete"
	print "add\t\t-add a task"
	print "clear\t\t-clear the output screen"
	print "exit\t\t-close program"

	p = threading.Thread(target = listener)
	p.start()
	cycleCount = 0
	while True:
		cycleCount += 1
		sys.stdout.flush()

		if not cycleCount % (REPRINT*60/DELAY):
			data = [CURRENTHEADER]+currentTasks+[COMPLETEDHEADER]+completedTasks
			write_to_file(f,'\n'.join(data))
			print "written!"

		if len(commands):
			command = commands[0]
			del commands[0]
			if command in "log" and command[0] == "l":
				print '\n'.join(data)

			elif command in "exit" and command[0] == "e":
				data = [CURRENTHEADER]+currentTasks+[COMPLETEDHEADER]+completedTasks
				write_to_file(f,'\n'.join(data))
				break

			else:
				print "Invalid command, " + command
		time.sleep(DELAY)

	try:
		f.close()
	except:
		pass

if __name__ == '__main__':
	main()