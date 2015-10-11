from django.db import models
import subprocess, threading
import os, glob
import string
from webgui.crontab import *

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

###
import random
from django.http import HttpResponse
import sqlite3
###



#class ContentTypeRestrictedFileField(FileField):
#    """
#    Same as FileField, but you can specify:
#        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
#        * max_upload_size - a number indicating the maximum file size allowed for upload.
#            2.5MB - 2621440
#            5MB - 5242880
#            10MB - 10485760
#            20MB - 20971520
#            50MB - 5242880
#            100MB 104857600
#            250MB - 214958080
#            500MB - 429916160
#"""
#    def __init__(self, *args, **kwargs):
#        self.content_types = kwargs.pop("content_types")
#        self.max_upload_size = kwargs.pop("max_upload_size")
#
#        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)
#
#    def clean(self, *args, **kwargs):
#        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
#
#        file = data.file
#        try:
#            content_type = file.content_type
#            if content_type in self.content_types:
#                if file._size > self.max_upload_size:
#                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
#            else:
#                raise forms.ValidationError(_('Filetype not supported.'))
#        except AttributeError:
#            pass
#
#        return data
#


class Projects(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    name = models.CharField(max_length=20, unique=True)
    company = models.CharField(max_length=20, blank=True, null=True)
#    creation_date = models.DateField(auto_now_add=True, null=True)
    creation_date = models.DateField(auto_now_add=True, auto_now=False)


#class Date(models.Model):
#    id = models.IntegerField(primary_key=True, blank=True)
#    date = models.DateField()


class Packages(models.Model):
    id = models.IntegerField(primary_key=True, blank=True)
    name = models.CharField(max_length=50)
    extension = models.CharField(max_length=3)
    gen_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    project = models.ForeignKey(Projects)

    #name = models.CharField(max_length=60)
    #path = models.FileField(upload_to='music', max_length=100)
    #artist = models.ForeignKey(Artist)
    #selected = models.BooleanField(default=False)

#class Alarmclock(models.Model):
#    id = models.IntegerField(primary_key=True, blank=True)
#    label = models.CharField(max_length=100)
#    hour = models.IntegerField(blank=True)
#    minute = models.IntegerField(blank=True)
#    period = models.CharField(max_length=100)    # cron syntax dow (day of week)
#    active = models.BooleanField(default=True)
#    snooze = models.IntegerField(blank=True)
#    mode = models.CharField(max_length=5, default='music')
#    webradio = models.ForeignKey(Webradio, blank=True, null=True, default=None)
    #webradio = generic.GenericForeignKey('
    ### added ###


#    def enable(self):
#        """
#        enable The alarm clock. Set it into the crontab
#        """
#        base_dir = os.path.dirname(os.path.dirname(__file__))
#        cron = Crontab()
#        cron.minute = self.minute
#        cron.hour = self.hour
#        cron.period = self.period
#        cron.comment = "piclodio "+str(self.id)
#        cron.command = "env DISPLAY=:0.0 python "+base_dir+"/runWebRadio.py "+str(self.id)
#        cron.create()
#
#    def disable(self):
#        """
#        disable the alarm clock. remove it from the crontab
#        """
#        cron = Crontab()
#        cron.comment = "piclodio "+str(self.id)
#        cron.remove()
#


class Player():
    """
    Class to play music with mplayer
    """
    def __init__(self):
        self.status = self.isStarted()



    def playmusic(self, music):
        if self.isStarted():
            self.stop()

        command = ("/usr/bin/mplayer "+settings.MEDIA_ROOT)
        path = music.path
        p = subprocess.Popen(command+str(music.path), shell=True)
        #p.wait()


    
    def playmusicrandom(self):
        ####### Select IDs from databases #######
        conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
        cur = conn.cursor()
        cur.execute("SELECT id FROM webgui_music")
        list_id = [row[0] for row in cur.fetchall()]

        selected_ids = random.sample(list_id, 1)
        #selected_id = random.choice(list_id)


        for i in (selected_ids):
            try:
                selectedmusic = Music.objects.get(selected=1)
                # unselect it
                selectedmusic.selected = False
                selectedmusic.save()
            except Music.DoesNotExist:
                #selectedmusic = None
		pass

            try:
                selectedartist = Artist.objects.get(selected=1)
                selectedartist.selected = False
                selectedartist.save()
            except Artist.DoesNotExist:
                #selectedartist = None
		pass

            music = Music.objects.get(id=i)
            artist_id = music.artist.id
            artist = Artist.objects.get(id=artist_id)

	    artist.selected = True
            artist.save()
            music.selected = True
            music.save()

        #music = Music.objects.get(id=i)
        #player = Player()
            self.playmusic(music)

#        player.playmusic(music)


#       s_id=random.choice(list_id)
#       music = Music.objects.get(id=s_id)
#       artist_id = music.artist.id
#       artist = Artist.objects.get(id=artist_id)
#       artist.selected = True
#       artist.save()
#       music.selected = True
#       music.save()
#
#       player.playmusic(music)




    def play(self, radio):
        # kill process if already running
        if self.isStarted():
            self.stop()

        url = radio.url  # get the url
        split_url = string.split(url, ".")
        size_tab = len(split_url)
        extension = split_url[size_tab-1]
        command = self.getthegoodcommand(extension)

        subprocess.Popen(command+radio.url, shell=True)

    def stop(self):
        """
        Kill mplayer process
        """
        p = subprocess.Popen("sudo killall mplayer", shell=True)
        p.communicate()
   
    def getthegoodcommand(self, extension):
        """
        switch extension, start mplay differently
        """
        return {
            'asx': "sudo /usr/bin/mplayer -playlist "

        }.get(extension, "sudo /usr/bin/mplayer ")  # default is mplayer

    def isStarted(self):
            # check number of process
            p = subprocess.Popen("sudo pgrep mplayer", stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            if output == "":
                    return False
            else:
                    return True


