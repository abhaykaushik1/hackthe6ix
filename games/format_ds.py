import cv2, random, time

from deepface import DeepFace

def match_emotion():
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    cap = cv2.VideoCapture(0)
    points = 0
    init_time = time.time()
    counter_timeout_text = init_time+1
    test_timeout = init_time+6
    
    guessed = False
    game = True
    emotion = 'happy'
    
    while game:
        try:
            ret, frame = cap.read()
            result = DeepFace.analyze(frame, actions = ['emotion'])
            gray = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray,1.1, 4)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)
            frame = cv2.rectangle(frame, (int(x),int(y+h)-20), (int(x)+40,int(y+h)), (0,0,255), -1)
            frame = cv2.putText(frame, result['dominant_emotion'], (int(x)+5,int(y+h)-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            
            if guessed:
                last_emotion = emotion
                emotion = random.choice(['calm', 'happy', 'sad', 'angry', 'fear'])
                while emotion == last_emotion:
                    emotion = random.choice(['calm', 'happy', 'sad', 'angry', 'fear'])
                guessed = False
            
            if emotion == result['dominant_emotion'] or (emotion == "calm" and result['dominant_emotion']=="neutral" and guessed==False):
                frame = cv2.putText(frame, 'Nice job!'.format(emotion), (int(frame.shape[0]/2),50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                points += 100
                guessed = True
                
            else:
                frame = cv2.putText(frame, 'Now show: {}'.format(emotion), (int(frame.shape[0]/2),50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            cv2.imshow('Original Video', frame)
            if cv2.waitKey(2) and 0xFF == ord('q'):
                cap = cv2.VideoCapture(1)
                break
        except ValueError:
            game = False
    
    cap.release()
    cv2.destroyAllWindows()
    return points