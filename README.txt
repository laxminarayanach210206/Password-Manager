secure_password_manager
│
├── app.py    #Flask backend
├── database.db  # generates empty db after running and stores the entered expences
├── key.key     #generate its own key after running app for encryption
│
├── templates
│   ├── login.html   #login page
│   └── dashboard.html  #dshboard page where passwords are encrypted
│   └── edit.html   #to edit the existing passwords and userid
|
└── static
    └── style.css

MASTER_USER = "admin"
MASTER_PASS = "1234"