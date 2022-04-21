from BioRecon.Log import Logdate
import cv2
import os
import time

dataPath = 'faces/'
imagePaths = os.listdir(dataPath)
print('imagePaths=',imagePaths)


face_recognizer = cv2.face.LBPHFaceRecognizer_create()

face_recognizer.read('modeloLBPHFace.xml')

faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
recognized = []

def Recognizer(frame):
	ret = True
	if ret == False: return
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	auxFrame = gray.copy()
	faces = faceClassif.detectMultiScale(gray,1.3,5)

	for (x,y,w,h) in faces:
		rostro = auxFrame[y:y+h,x:x+w]
		rostro = cv2.resize(rostro,(150,150),interpolation= cv2.INTER_CUBIC)
		result = face_recognizer.predict(rostro)

		if result[1] < 70:
			recognized.append(result[0])
			if len(recognized) == 40:
				return(MostFrequent(recognized))
			cv2.putText(frame,'{}'.format(imagePaths[result[0]]),(x,y-25),2,1.1,(219,79,203),1,cv2.LINE_AA)
			cv2.rectangle(frame, (x,y),(x+w,y+h),(219,79,203),2)
		else:
			cv2.putText(frame,'Desconocido',(x,y-20),2,0.8,(0,0,255),1,cv2.LINE_AA)
			cv2.rectangle(frame, (x,y),(x+w,y+h),(0,0,255),2)

def MostFrequent(recognized):
    i = max(set(recognized), key = recognized.count)
    uid = imagePaths[i]
    print(Logdate(), "[LOG]", f"recognized uid {uid}")
    recognized.clear()
    return uid

cv2.destroyAllWindows()
