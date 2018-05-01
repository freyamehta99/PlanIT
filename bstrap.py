from todoflask import *

create_all()

# add an user
u1 = auth.User(username='admin', admin=True, active=True)
u1.email = 'admin@admin.com'
u1.set_password('admin')
u1.save()

#add another user
u2 = auth.User(username='freya', admin=True, active=True)
u2.email = 'freyamehta99@yahoo.com'
u2.set_password('freya')
u2.save()

u2 = auth.User(username='lalitha', admin=True, active=True)
u2.email = 'valk@gmail.com'
u2.set_password('lalitha')
u2.save()
u2 = auth.User(username='harshit', admin=True, active=True)
u2.email = 'harshit@ta.com'
u2.set_password('harshit')
u2.save()
u2 = auth.User(username='user', admin=True, active=True)
u2.email = 'user@random.com'
u2.set_password('userpass')
u2.save()

