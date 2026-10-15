from django.contrib.auth.models import User 


def register_user(username, email, password): 
    if User.objects.filter(username=username).exists(): 
        raise ValueError("Username already exists") 

    if User.objects.filter(email=email).exists(): 
        raise ValueError("Email already exists") 

    return User.objects.create_user( 
        username=username, 
        email=email, 
        password=password, 
    ) 
