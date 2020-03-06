import smtplib 

# creates SMTP session 
s = smtplib.SMTP('smtp.gmail.com', 587) 

# start TLS for security 
s.starttls() 

# Authentication 
s.login("mattugraz@gmail.com", "sanrafael88!") 

# message to be sent 
message = "Message_you_need_to_send"

# sending the mail 
s.sendmail("mattugraz@gmail.com", "mattugraz@gmail.com", message) 

# terminating the session 
s.quit() 

