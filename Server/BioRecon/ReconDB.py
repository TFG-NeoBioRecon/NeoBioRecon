import mysql.connector

def Query(user, room):
	user = str(user)
	room = room.decode('utf-8')
	mydb = mysql.connector.connect(
	host="localhost",
	user="biorecondb",
	password="g>m2keALñ&c>&NS",
	database= 'biorecondb01'
	)
	mycursor = mydb.cursor()
	mycursor.execute("SELECT CASE WHEN EXISTS ( SELECT * FROM users JOIN rol_usr ON users.id=rol_usr.usr_id JOIN rol_room ON rol_usr.rol_id = rol_room.rom_id WHERE users.uid ='"+ user +"' AND rol_room.rom_id ="+ room +") THEN \'TRUE\' ELSE \'FALSE\' END")

	result = (mycursor.fetchall())
	mycursor.close()
	if "TRUE" in result[0]:
		return True
	else:
		return False