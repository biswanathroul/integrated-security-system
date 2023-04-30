import time
import RPi.GPIO as GPIO
import cv2
import face_recognition
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Set up GPIO pins for sensors and alarms
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)  # PIR sensor
GPIO.setup(12, GPIO.OUT)  # Alarm
GPIO.setup(13, GPIO.IN)  # Door sensor

# Set up email account for sending alerts
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'your_email@gmail.com'
smtp_password = 'your_password'
sender_email = 'your_email@gmail.com'
recipient_email = 'recipient_email@gmail.com'

# Load images for facial recognition
known_image = face_recognition.load_image_file('known_face.jpg')
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# Initialize video camera
cap = cv2.VideoCapture(0)

while True:
    # Check PIR sensor
    if GPIO.input(11):
        print('Motion detected')

        # Start video capture
        ret, frame = cap.read()

        # Detect faces in the video frame
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            # Encode faces and compare to known face
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            match = face_recognition.compare_faces([known_face_encoding], face_encodings[0])[0]
            if match:
                print('Face recognized')

                # Send email with image attachment
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = 'Security Alert'
                msg.attach(MIMEText('Motion detected and face recognized'))
                img = cv2.imencode('.jpg', frame)[1]
                image = MIMEImage(img)
                msg.attach(image)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(sender_email, recipient_email, msg.as_string())

                # Turn on alarm
                GPIO.output(12, GPIO.HIGH)
                time.sleep(5)
                GPIO.output(12, GPIO.LOW)

            else:
                print('Unknown face')
        else:
            print('No face detected')

    # Check door sensor
    if GPIO.input(13):
        print('Door opened')

        # Send email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'Security Alert'
        msg.attach(MIMEText('Door opened'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

    time.sleep(1)

# Clean up GPIO pins and video capture
GPIO.cleanup()
cap.release()
cv2.destroyAllWindows()
