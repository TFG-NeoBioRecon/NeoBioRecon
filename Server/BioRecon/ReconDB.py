import mysql.connector
import secrets
import time
from BioRecon.Email import SendMail
def Query(user, room):
	user = str(user)
	room = room.decode('utf-8')
	dbconn = mysql.connector.connect(
	host="localhost",
	user="biorecondb",
	password="g>m2keALñ&c>&NS",
	database= 'biorecondb01'
	)
	mycursor = dbconn.cursor()
	statement = "SELECT CASE WHEN EXISTS ( SELECT * FROM users JOIN rol_usr ON users.id=rol_usr.usr_id JOIN rol_room ON rol_usr.rol_id = rol_room.rol_id WHERE users.uid ='"+user+"' AND rol_room.rom_id ="+room+") THEN (SELECT rol.auth_level FROM rol JOIN rol_usr ON rol.id=rol_usr.rol_id JOIN users ON rol_usr.usr_id = users.id WHERE users.uid ='"+user+"') ELSE 'FALSE' END"
	#print(statement)
	mycursor.execute(statement)
	#mycursor.execute("SELECT CASE WHEN EXISTS ( SELECT * FROM users JOIN rol_usr ON users.id=rol_usr.usr_id JOIN rol_room ON rol_usr.rol_id = rol_room.rom_id WHERE users.uid ='"+ user +"' AND rol_room.rom_id ="+ room +") THEN \'TRUE\' ELSE \'FALSE\' END")
	#print(statement)
	#print("SELECT CASE WHEN EXISTS ( SELECT * FROM users JOIN rol_usr ON users.id=rol_usr.usr_id JOIN rol_room ON rol_usr.rol_id = rol_room.rom_id WHERE users.uid ='"+ user +"' AND rol_room.rom_id ="+ room +") THEN \'TRUE\' ELSE \'FALSE\' END")
	result = (mycursor.fetchall())
	if "FALSE" in str(result[0]):
		return False
	elif "'1'" in str(result[0]):
		return True
	elif "'2'" in str(result[0]):
		token = str(secrets.token_hex(32))
		mycursor.execute("SELECT email FROM users WHERE uid='"+user+"'")
		result = (mycursor.fetchone()) #User email
		SendMail("biorecondev@gmail.com",result[0],user,token,room)
		return OTP(user,token)
		mycursor.close()
	dbconn.commit()
	dbconn.close()
	

def OTP(user,token):
	dbconn = mysql.connector.connect(
	host="localhost",
	user="biorecondb",
	password="g>m2keALñ&c>&NS",
	database= 'biorecondb01'
	)
	mycursor = dbconn.cursor()
	statement = "INSERT INTO otp (usr_id,token) VALUES ((SELECT id FROM users WHERE uid='"+user+"'),'"+token+"')"
	mycursor.execute(statement)
	dbconn.commit()
	t_end = time.time() +10 #Wait x s for user to click on otp link
	statement = "SELECT authed FROM otp JOIN users ON otp.usr_id=users.id WHERE users.uid='"+user+"'"
	mycursor.close()
	while time.time() < t_end:
		dbconn.commit()
		mycursor = dbconn.cursor()
		mycursor.execute(statement)
		result = (mycursor.fetchall())
		mycursor.close()
		if "1" in str(result[0]):
			statement = "DELETE FROM otp WHERE usr_id = (SELECT id FROM users WHERE uid='"+user+"')"
			mycursor = dbconn.cursor()
			mycursor.execute(statement)
			dbconn.commit()
			return True
		mycursor.close()
	statement = "DELETE FROM otp WHERE usr_id = (SELECT id FROM users WHERE uid='"+user+"')"
	mycursor = dbconn.cursor()
	mycursor.execute(statement)
	dbconn.commit()
	dbconn.close()
	return False
	
def RoomLog(user, room):
	user = str(user)
	room = room.decode('utf-8')
	dbconn = mysql.connector.connect(
	host="localhost",
	user="biorecondb",
	password="g>m2keALñ&c>&NS",
	database= 'biorecondb01'
	)
	mycursor = dbconn.cursor()
	mycursor.execute("INSERT INTO room_logs (rom_id,usr_id) VALUES ("+room+",(SELECT id FROM users WHERE uid = '"+user+"'))")
	dbconn.commit()
	mycursor.close()
	dbconn.close()