import pickle

from django.db import models


class File(models.Model):
    """Model for files throughout"""
    path = models.CharField(max_length=400, db_index=True, unique = True)

    def __unicode__(self):
        return self.path


class Tag(models.Model):
    """Model to add tags to the Change model"""
    value = models.CharField(max_length = 50, db_index = True, unique = True)

    def __unicode__(self):
        return self.value


class Change(models.Model):
    """Model for buildbot.changes.changes.Change"""
    number = models.PositiveIntegerField(primary_key = True)
    branch = models.CharField(max_length = 20, null = True, blank = True)
    revision = models.CharField(max_length = 50, null = True, blank = True)
    who = models.CharField(max_length = 100, null = True, blank = True
                           db_index = True)
    files = models.ManyToMany(File)
    comments = models.TextField()
    when = models.DateTimeField()
    tags = models.ManyToMany(Tag)

    def __unicode__(self):
        rv = u'Change %d' % self.number
        if self.branch:
            rv += ', ' + self.branch
        if self.tags:
            rv += '(%s)' + ', '.join(map(unicode, self.tags.all()))


class Property(models.Model):
    """Helper model for build properties.

    To support complex property values, they are internally pickled.
    """
    name            = models.CharField(max_length = 20, db_index = True)
    value           = models.TextField()
    unique_together = (('name', 'value'),)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.value)


class Builder(models.Model):
    """Model for buildbot.status.builder.BuilderStatus"""
    name     = models.CharField(max_length = 50, unique = True, db_index = True)
    category = models.CharField(max_length = 30, null = True, blank = True,
                                db_index = True)
    bigState = models.CharField(max_length = 30, null = True, blank = True)

    def __unicode__(self):
        return u'Builder <%s>' % self.name


class Build(models.Model):
    """Model for buildbot..status.builder.Build

    TODO: BuildSteps
    """
    buildnumber = models.IntegerField(null = True, db_index = True)
    properties  = models.ManyToManyField(Property, related_name = 'builds')
    builder     = models.ForeignKey(Builder, related_name = 'builds')
    slavename   = models.CharField(max_length = 50, null=True, blank = True)
    starttime   = models.DateTimeField(null = True, blank = True)
    endtime     = models.DateTimeField(null = True, blank = True)
    results     = models.IntegerField(null = True)
    reason      = models.CharField(max_length = 50, null = True, blank = True)
    changes     = models.ManyToManyField(Change, null = True,
                                         related_name = 'builds')

    def setProperty(self, name, value):
        value = pickle.dumps(value)
        try:
            # First, see if we have the property, or a property of that name,
            # at least.
            prop = self.properties.get(name=name)
            if prop.value == value:
                # we already know this, we're done
                return
            if prop.builds.count() < 2:
                # this is our own property, set the new value
                prop.value = value
                prop.save()
                return
            # otherwise, unbind the property, and fake a DoesNotExist
            self.properties.remove(prop)
            raise Property.DoesNotExist(name)
        except Property.DoesNotExist:
            prop, created = Property.objects.get_or_create(name = name,
                                                           value = value)
        self.properties.add(prop)
        self.save()

      def getProperty(self, name):
          try:
              prop = self.properties.get(name = name)
          except Property.DoesNotExist:
              raise KeyError(name)
          return pickle.loads(prop.value)

      def __unicode__(self):
          v = self.builder.name
          if self.buildnumber is not None:
              v += ': %d' % self.buildnumber
          return v


class Step(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField(null = True, blank = True)
    text2 = models.TextField(null = True, blank = True)
    build = models.ForeignKey(Build, related_name = 'steps')


class URL(models.Model):
    name = models.CharField(max_length = 20)
    url = models.URLField()
    step = models.ForeignKey(Step, related_name = 'urls')


class Log(models.Model):
    filename = models.CharField(max_length = 200, unique = True)
    step = models.ForeignKey(Step, related_name = 'logs')
    isFinished = models.BooleanField(default = False)
    isHTML = models.BooleanField(default = False)

    def __unicode__(self):
        return self.filename

        
