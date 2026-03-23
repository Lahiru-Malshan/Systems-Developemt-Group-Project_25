import bcrypt
from login import login
from register import register_user
# create test user (if not exists) then verify
print(register_user("admin", "admin!", "A","B","a@b.c"))
print(login("admin", "admin!"))  # should return user dict
print(login("admin", "wrong"))      # should return "Invalid"

print(register_user("tenant", "tenant!", "C","D","c@d.e"))

