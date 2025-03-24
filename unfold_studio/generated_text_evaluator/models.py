from django.db import models

# Create your models here.

class TripletType:
    DIRECT_CONTINUE = "DIRECT_CONTINUE"
    BRIDGE_AND_CONTINUE = "BRIDGE_AND_CONTINUE"
    NEEDS_INPUT = "NEEDS_INPUT"
    INVALID_USER_INPUT = "INVALID_USER_INPUT"
