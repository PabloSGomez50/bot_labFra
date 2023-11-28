import smtplib
from email.message import EmailMessage
import os

msg = EmailMessage()
mail = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASSWORD").replace(' ', '')

# Contenido
msg['From']=mail
msg['To']="pablosgomez50@gmail.com"
msg['Subject']= "Probando mandar mails!"
cuerpo_del_mail = 'Test verificando github actions'
msg.set_content(cuerpo_del_mail)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(mail, password)

# enviar
server.send_message(msg)
server.quit()
