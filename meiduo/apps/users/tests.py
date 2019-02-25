from django.test import TestCase
from random import randint
# Create your tests here.
sms_code = '%06d' % randint(0, 999999)
print(sms_code)