from django.db import models

# Create your models here.
class Emp(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    def __str__(self):
        return self.name
    
class Student(models.Model):
    name = models.CharField(max_length=100)
    marks = models.IntegerField()
    def __str__(self):
        return self.name
    
class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()

    def __str__(self) -> str:
        return self.name
    
class Employee(models.Model):
    eno = models.IntegerField()
    ename = models.CharField(max_length=100)
    esal = models.FloatField()

    def __str__(self) -> str:
        return self.ename
    
class ContactInfo(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)

    class Meta:
        abstract = True

class Stu(ContactInfo):
    roll = models.IntegerField()
    course = models.CharField(max_length=100)

class Teacher(ContactInfo):
    subject = models.CharField(max_length=100)
    salary = models.IntegerField()

class BasicModel(models.Model):
    f1 = models.CharField(max_length=100)
    f2 = models.IntegerField()
    f3 = models.FloatField()

class StrandardModel(BasicModel):
    f4 = models.CharField(max_length=100)
    f5 = models.IntegerField()
    f6 = models.FloatField()