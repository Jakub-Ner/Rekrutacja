# sudo python -m smtpd -n -c DebuggingServer localhost:25
from mailer import Message
import smtplib

class Mail:
    def __init__(self, to_adress, subject, content):
        self.to_adress = to_adress
        self.subject = subject
        self.content = self.editing(content)
        msg = self.build_email()
        self.send_email(msg, 'localhost', 25)

    def build_email(self):
        message = Message()
        message.From = "kulrestauracja-noreply@gmail.com"
        message.To = self.to_adress
        message.Subject = self.subject
        message.Body = self.content
        return message

    def send_email(self, msg, host='', port=0):
        s = smtplib.SMTP(host, port, local_hostname="smtp.mydomain.com")
        result = s.sendmail(msg.From, msg.To, msg.as_string())
        s.quit()
        return result

    def editing(self, content):
        message ="Hello! \nHere's Your data:\n\n"
        for item in content:
            if item != "id" and item != "email" and item != '_sa_instance_state':
                message += str(item) +": "+ str(content[item])+"\n"
        message+="\nhave a nice day!"
        return message
            
