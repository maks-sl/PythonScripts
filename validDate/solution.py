# max day for each month
maxDay = [31,28,31,30,31,30,31,31,30,31,30,31]
# message on error
errorMsg = 'Ambiguous'

def validDate(a):
        a = sorted(a)
        if (a[0] > 12) :
                return errorMsg
        if (a[1] <= 12 and a[1] != a[0]) :
                return errorMsg
        if (a[1] > maxDay[a[0]-1]) :
                return errorMsg
        if (a[2] <= maxDay[a[0]-1] and a[2] != a[1]) :
                return errorMsg
        return '/'.join(list(map(str, a))) 

while True :
	toCompare = []
	print('Fill array using integer between 1 and 99 to start ')
	numItems = 0
	while numItems < 3 :
		welcome = '['+str(numItems)+'/3 filled]. Enter value or "exit": '
		msgIn = input(welcome)
		if msgIn.lower() == 'exit' :
			exit(0)
		try:
			num = int(msgIn)
			if 0 < num < 100 :
				toCompare.append(num)
				numItems += 1
			else :
				print('Value must be int between 1 and 99')
		except ValueError:
			print('Not valid value type. Try again using int')
	print('Ok. Working...')
	result = validDate(toCompare)
	print('Out: ' + result)
	msg = input('Try again? (y/n)')
	if msg == 'n' :
		exit(0)
	
