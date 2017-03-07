from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length = 250)
    is_active = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Task(models.Model):
    text = models.CharField(max_length = 250)
    state = models.CharField(max_length = 20, default = 'NEW')
    owner = models.ForeignKey(Customer)
    is_private = models.BooleanField(default = True)
    created = models.DateTimeField(auto_now_add = True)
    changed = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return "%s: %s,%s" % (self.text, self.owner, self.created)
