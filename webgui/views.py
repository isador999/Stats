#-*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from webgui.models import Packages, Projects
from webgui.forms import ProjectForm
import os, glob
#import subprocess
from time import strftime
import time
import shutil
import urllib
import simplejson
from chartit import DataPool, Chart
#from graphos.sources.simple import SimpleDataSource
##from graphos.sources.model import ModelDataSource
#from graphos.renderers import flot
##### 
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf import settings
#import json
import threading


def homepage(request):

    #clock = strftime("%H:%M:%S")
    date = strftime("%A %d %b %Y")


    try:
       lastpackages = Packages.objects.reverse()[:5]
    except Packages.DoesNotExist:
        lastpackages = None



    try:
	listprojects = Projects.objects.all()
    except Projects.DoesNotExist:
        listprojects = None

    return render(request, 'homepage.html', {'listprojects': listprojects,
					     'lastpackages': lastpackages,
                                             #'clock': clock,
                                             'date': date})


def addproject(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ProjectForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # save web radio
            #form.instance.selected = False
	    src = settings.PROJECTS_DIR+'template'
	    dest = settings.PROJECTS_DIR+request.POST['name']

            # forced to place all in one 'try' block, cause to error :
            # "Local var referenced before assignment" 
            # (in the case where 'return' are placed with 'if e_msg' , after the try block
	    try:
		shutil.copytree(src, dest)
                form.save()
                return redirect('webgui.views.homepage')
	    except shutil.Error:
		#print('Directory not copied. Error : %s' % e)
		e_msg=('Directory Not Copied. Shutil Module Error : %s')
                return render(request, 'addproject.html', {'e_msg': e_msg })
	    except OSError:
		#print('Directory not copied. Error : %s' % e)
		e_msg=('Directory Not Copied. OS Error : Maybe the Project Dir already exists')
                return render(request, 'addproject.html', {'e_msg': e_msg })

    else:
        form = ProjectForm()

    return render(request, 'addproject.html', {'form': form})



def delproject(request, id):
    project = Projects.objects.get(id=id)
    project.delete()
    try:
        shutil.rmtree(settings.PROJECTS_DIR+project.name)
    except:
        return redirect('webgui.views.homepage')

    return redirect('webgui.views.homepage')


def listpackages(request, id):
    project = Projects.objects.get(id=id)
    listpkgs = Packages.objects.filter(project=id)
    #listpkgs = Packages.objects.get(project_id=id)

    return render(request, 'listpackages.html', {'listpkgs': listpkgs, 'project': project})




def displaystats(request):
    try:
        listpackages = Packages.objects.all()
    except Packages.DoesNotExist:
        listpackages = None

#    data = [
#    ['NbPackages', 'Projects'],
#    ['2004', 1000],
#    ['2005', 1170],
#    ['2006', 660],
#    ['2007', 1030]
#    ]
    try:
        listprojects = Projects.objects.all()
    except Projects.DoesNotExist:
        listprojects = None

    #line_chart = flot.LineChart(SimpleDataSource(data=data))
    #data_source = ModelDataSource(listpackages, fields=['name', 'extension'])
    #data_source = ModelDataSource(Packages, fields=['name', 'extension'])
    #line_chart = flot.LineChart(data_source, options={'title': "Project Stats"})

#    line_chart = flot.LineChart(SimpleDataSource(data=data),options={'series':{'color':'orange'}, 'lines': {'lineWidth': 10, 'fill':40, 'fillColor': {'colors':["rgba(70, 70, 120, 5)","rgba(255, 255, 255,5)"]} }, 'points':{'symbol':'circle'},'xaxis':{'mode':'time', 'timezone':'browser', 'axisLabel':'Date Time', 'axisLabelUseCanvas':'true', 'axisLabelFontSizePixels': 20,'axisLabelFontFamily':'Arial','color':'red'},'yaxis':{'min':0, 'max':75, 'tickSize': 15, 'axisLabel':'Centimeters', 'axisLabelUseCanvas':'true', 'axisLabelFontSizePixels': 20,'axisLabelFontFamily':'Arial'},'grid':{'color':800}})

    projectsdata = \
        DataPool(
	  series=
	    [{'options': {
	      'source': Projects.objects.all()},
	     'terms': [
	        'id',
		'name','company'
	    ]}])

    packagesdata = \
        DataPool(
	  series=
	    [{'options': {
	      'source': Packages.objects.all()},
	     'terms': [
	        'id',
		'name','extension'
	    ]}])

    chtpject = Chart(
        datasource = projectsdata,
	series_options =
	  [{'options':{
	      'type': 'line',
	      'stacking': False},
	 'terms':{
	     'id': [
	       'name','company']
	     }}],

	     chart_options =
	         {'title': {
		     'text': 'Sample Graph'},
		 'xAxis': {
		     'title':{'text': 'Projects'}},
		 'yAxis': {
		     'title':{'text': 'Packages'}}})

    chtpkg = Chart(
        datasource = packagesdata,
	series_options =
	  [{'options':{
	      'type': 'line',
	      'stacking': False},
	 'terms':{
	     'id': [
	       'name','extension']
	     }}],

	     chart_options =
	         {'title': {
		     'text': 'PKG Graph'},
		 'xAxis': {
		     'title':{'text': 'Packages'}}})


    return render_to_response('stats.html',{'chtpject': chtpject, 'chtpkg': chtpkg, 'listpackages': listpackages})

    #return render(request, 'stats.html', {'line_chart': line_chart, 'listpackages': listpackages})
    #return render(request, 'stats.html', {'listpackages': listpackages})



def playmusic(request, id):
    try:
        selectedmusic = Music.objects.get(selected=1)
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

    music = Music.objects.get(id=id)
    artist_id = music.artist.id
    artist = Artist.objects.get(id=artist_id)

    artist.selected = True
    artist.save()

    music.selected = True
    music.save()
    player = Player()
    player.playmusic(music)

    time.sleep(1)

    if not player.isStarted():  # then start the backup mp3
        player = Player()
        music = Music
        music.path = 'mplayer /srv/fichiers/backup.mp3'
        player.playmusic(music)

    return redirect('webgui.views.homepage')



def playmusicrandom(request):
    player = Player()
    #player.playmusicrandom()
    t = threading.Thread(target=player.playmusicrandom)
    t.setDaemon(True)
    t.start()
    time.sleep(1.5)
    return redirect('webgui.views.homepage')


##################################################################
##################################################################

def multiple_uploader(request, id):
    if request.POST:
        if request.FILES == None:
            raise Http404("No objects uploaded")
        f = request.FILES['file']

        a = Artist.objects.get(id=id)
        b = Music()

        b.artist = a
        b.selected = False
        b.name = f.name
        b.path.save(f.name, f)

        result = [{'name': f.name,
#                  'size': f.size,
#                  'url': a.path.url,
                 },]

        #response_data = simplejson.dumps(result)
	response_data = json.dumps(result)
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, content_type=mimetype)
    else:
        return HttpResponse('Only POST accepted')



def webradio(request):
    listradio = Webradio.objects.all()
    return render(request, 'webradio.html', {'listradio': listradio})


def update_webradio(request, id_webradio):
    selected_webradio = get_object_or_404(Webradio, id=id_webradio)
    form = WebradioForm(request.POST or None, instance=selected_webradio)
    if form.is_valid():
        form.save()
        return redirect('webgui.views.webradio')

    return render(request, 'update_webradio.html', {'form': form, 'radio': selected_webradio})



def delete_web_radio(request, id_radio):
    radio = Webradio.objects.get(id=id_radio)
    radio.delete()
    return redirect('webgui.views.webradio')


def options(request):
    # get sound info
    #am = AudioManager()
    #current_volume = am.get_percent_volume()
    #current_mute = am.get_mute_status()

    # get actual mp3 backup file
    #actual_backup = _get_mp3_in_backup_folder()

    if request.method == 'POST':
        form = BackupMP3Form(request.POST, request.FILES)
        if form.is_valid():
           # remove backup save in database
            BackupMP3.objects.all().delete()
            # remove file in backup folder
            _delete_mp3_from_backup_folder()
            form.save()
            return redirect('webgui.views.options')
    else:
        form = BackupMP3Form()

    return render(request, 'options.html', {'currentVolume': current_volume,
                                            'currentMute': current_mute,
                                            'form': form,
                                            'backup': actual_backup})



################ MY PERSONNAL FUNCTION 'OPTIONS' ################
#################################################################
#def options(request):
#    soundPath = os.path.dirname(os.path.abspath(__file__))+"/utils/picsound.sh"
#    currentVolume = subprocess.check_output([soundPath, "--getLevel"])
#    currentMute = subprocess.check_output([soundPath, "--getSwitch"])

#    timePath = os.path.dirname(os.path.abspath(__file__))+"/utils/time.sh"
#    currentTime = subprocess.check_output([timePath, "--get"])
#    return render(request,'options.html', {'currentVolume':currentVolume,'currentMute':currentMute,'currentTime':currentTime,'rangeHour':range(24),'rangeMinute':range(60) })
#################"

def debug(request):
    todisplay = 'hello world debug'
    return render(request, 'debug.html', {'todisplay': todisplay})


def play(request, id_radio):
    # get actual selected radio if exist
    try:
        selectedradio = Webradio.objects.get(selected=1)
        # unselect it
        selectedradio.selected = False
        selectedradio.save()
    except Webradio.DoesNotExist:
        pass

    # set the new selected radio
    radio = Webradio.objects.get(id=id_radio)
    radio.selected = True
    radio.save()
    player = Player()
    # check if url is available
    try:
        http_code = urllib.urlopen(radio.url).getcode()
    except IOError:
        http_code = 0
    print http_code
    if http_code == 200:
        player.play(radio)
    else:
        # play backup MP3
        radio.url = 'mplayer backup_mp3/*'
        player.play(radio)

    return redirect('webgui.views.homepage')


def stop(request):
    player = Player()
    player.stop()
    time.sleep(1)
    return redirect('webgui.views.homepage')


def alarmclock(request):
    list_alarm = Alarmclock.objects.all()
    return render(request, 'alarmclock.html', {'listAlarm': list_alarm})


def activeAlarmClock(request, id):
    alarmclock = Alarmclock.objects.get(id=id)
    if not alarmclock.active:
        alarmclock.active = True
        alarmclock.enable()
    else:
        alarmclock.active = False
        alarmclock.disable()

    alarmclock.save()
    return redirect('webgui.views.alarmclock')



def create_alarmclock(request):
    if request.method == 'POST':
        form = AlarmClockForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # convert period
            period = form.cleaned_data['period']
            period_crontab = _convert_period_to_crontab(period)
            form.period = _convert_period_to_crontab(period)
            # save in database
            form.save()
            # set the cron
            alarmclock = Alarmclock.objects.latest('id')
            alarmclock.period = period_crontab
            alarmclock.active = True
            alarmclock.enable()
            alarmclock.save()

            return redirect('webgui.views.alarmclock')
    else:
        form = AlarmClockForm()  # An unbound form
    return render(request, 'create_alarmclock.html', {'form': form})



def update_alarmclock(request, id_alarmclock):
    selected_webradio = get_object_or_404(Alarmclock, id=id_alarmclock)
    form = AlarmClockForm(request.POST or None, instance=selected_webradio)
    if form.is_valid():
        # convert period
        period = form.cleaned_data['period']
        period_crontab = _convert_period_to_crontab(period)
        form.period = period_crontab
        # save in database
        form.save()
        # set the cron
        alarmclock = Alarmclock.objects.latest('id')
        alarmclock.period = period_crontab
        # disble to remove from crontab
        alarmclock.disable()
        # then enable to create it again
        alarmclock.enable()
        alarmclock.save()

        return redirect('webgui.views.alarmclock')

    return render(request, 'update_alarmclock.html', {'form': form, 'alarmclock': selected_webradio})


def deleteAlarmClock(request, id_alarmclock):
    target_alarmclock = Alarmclock.objects.get(id=id_alarmclock)
    target_alarmclock.disable()
    target_alarmclock.delete()
    return redirect('webgui.views.alarmclock')




@csrf_exempt
def timeset(request):
    if request.method == 'POST':
        hour = request.POST['hour']
        minute = request.POST['minute']

        hour = str(hour)
        minute = str(minute)

        scriptPath = os.path.dirname(os.path.abspath(__file__))+"/utils/time.sh"
        subprocess.call(["sudo", scriptPath, "--set", hour, minute])

        url = request.build_absolute_uri('http://reveil/options')

        json_data = json.dumps({"HTTPRESPONSE":url})
        return HttpResponse(json_data, mimetype="application/json")

    else:
        return render(request, 'options.html')



def volumeup(request, count):
    am = AudioManager()
    am.volume_up()
    return redirect('webgui.views.options')


def volumedown(request, count):
    am = AudioManager()
    am.volume_down()
    return redirect('webgui.views.options')


def volumeset(request, volume):
    am = AudioManager()
    am.set_volume(int(volume))
    return redirect('webgui.views.options')


def volumetmute(request):
    am = AudioManager()
    am.togglemute()
    return redirect('webgui.views.options')


def _convert_period_to_crontab(period):
    # decode unicode
    period_decoded = [str(x) for x in period]

    # transform period into crontab compatible
    period_crontab = ""
    first_time = True  # first time we add a value
    for p in period_decoded:
        if first_time:  # we do not add ","
            period_crontab += str(p)
            first_time = False
        else:
            period_crontab += ","
            period_crontab += str(p)
    return period_crontab


def _get_mp3_in_backup_folder():
    path = os.path.dirname(os.path.abspath(__file__))+"/../backup_mp3"
    mp3 = os.listdir(path)
    if mp3:
        return mp3[0]

def _delete_mp3_from_backup_folder():
    path = os.path.dirname(os.path.abspath(__file__))+"/../backup_mp3/*"
    filelist = glob.glob(path)
    for f in filelist:
        os.remove(f)
