# -*- coding: UTF-8 -*-
# Variables for the Agenda add-on
# written by Abel Passos do Nascimento Jr. <abel.passos@gmail.com>, Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes <ampa4374@gmail.com> and 
# Copyright (C) 2022-2023 Abel Passos do Nascimento Jr. <abel.passos@gmail.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# import the necessary modules.
import ui
import wx
import os
import winsound
import globalVars
import gui
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from gui import guiHelper
import core
import config
import glob
import addonHandler
from .manageDatabase import *
from .nextAppointments import nextAppointments
from .convertdate import persian

# To start translation process
addonHandler.initTranslation()

def getOurAddon():
	return addonHandler.getCodeAddon()

ourAddon = getOurAddon()

def initConfiguration():
	confspec = {
		"show" : "boolean(default=True)",
		"days" : "integer(1, 30, default=1)",
		"alarmSoundToUse" : "string(default="")",
		"playSound" : "boolean(default=False)",
		"soundToUse" : "string(default="")",
		"calendar" : "string(default="")",
		"path" : "string(default="")",
		"altPath" : "string(default="")",
		"xx" : "string(default="")",
	}
	config.conf.spec[ourAddon.name] = confspec

initConfiguration()

# Global variables
calendars = [_("Gregorian (Default)"), _("Persian")]
months = [_("December"), _("November"), _("October"), _("September"), _("August"), _("July"), _("June"), _("May"), _("April"), _("March"), _("February"), _("January")]
persianMonths = [_("Esfand"), _("Bahman"), _("Dey"), _("Azar"), _("Aban"), _("Mehr"), _("Shahrivar"), _("Mordad"), _("Tir"), _("Khordad"), _("Ordibehesht"), _("Farvardin")]
weekDays = [_("Monday"), _("tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday"), _("Sunday")]
frequency = [_('None'), _("Daily"), _("Weekly"), _("Biweekly"), _("Monthly"), _("Twomonthly"), _("Threemontly"), _("Fourmontly"), _("Sixmonthly"), _("Anualy")]
flagAlarmDayAfter = False if config.conf[ourAddon.name]["show"] else True
flagPauseAlarm=False
endAlarms = False
dictNextAlarms={}
PluginDir = os.path.join(addonHandler.getCodeAddon().path, "globalPlugins", "agenda")
SoundsDir = os.path.join(PluginDir, "sounds")
soundsList = [os.path.split(path)[-1] for path in glob.glob(os.path.join(SoundsDir, '*.wav'))]

# Gets the maximum day of the month passed to the function
def maxDayMonth(year, month):
	from . configPanel import calendarToUse
	dayMax =0
	if calendarToUse == _("Gregorian (Default)"):
		if month in [1, 3, 5, 7, 8, 10, 12]:
			dayMax=31
		elif month in [4, 6, 9, 11]:
			dayMax=30
		else:
			if (year/4)==(year//4) and (year/100)!=(year//100):
				dayMax=29
			else:	 
				dayMax=28
		return dayMax
	elif calendarToUse == _("Persian"):
		if month in [1, 2, 3, 4, 5, 6]:
			dayMax=31
		elif month in [7, 8, 9, 10, 11]:
			dayMax=30
		else:
			if persian.leap(year):
				dayMax=30
			else:	 
				dayMax=29
		return dayMax

# Adjust the week day to be correct in persian calendar
def gregorianWeekDayToPersian(day):
				weekDay = day
				persianWeekDay = weekDays.index(weekDay)+1
				if persianWeekDay == 7:
					persianWeekDay = 0
				persianWeekDay = weekDays[persianWeekDay]
				return persianWeekDay

def threadAlarm ():
	global dictNextAlarms
	# check every 3 seconds if alarm exists
	while not endAlarms:
		while  flagPauseAlarm:
			time.sleep(3)
		m = int(datetime.datetime.strftime(datetime.datetime.now(), '%M'))
		x = m	 
		while x==m:
			m = datetime.datetime.strftime(datetime.datetime.now(), '%M')
			#Check every 5 seconds if the minutes value was changed
			time.sleep(5)
		# if minute increase, check dictionary
		selfNow = datetime.datetime.now()
		from .configPanel import nDays
		nextDays = selfNow + datetime.timedelta(days=nDays-1)
		justNow = int(datetime.datetime.strftime(selfNow, '%Y%m%d%H%M'))
		tomorrowStart = int(datetime.datetime.strftime(nextDays, '%Y%m%d')+'0000')
		tomorrowEnd = int(datetime.datetime.strftime(nextDays, '%Y%m%d')+'2359')
		if len(dictNextAlarms) != 0:
			oneHourBefore = int(datetime.datetime.strftime(selfNow + datetime.timedelta(minutes=60), '%Y%m%d%H%M')) 
			halfHourBefore = int(datetime.datetime.strftime(selfNow + datetime.timedelta(minutes=30), '%Y%m%d%H%M')) 
			fifteenMinutesBefore = int(datetime.datetime.strftime(selfNow + datetime.timedelta(minutes=15), '%Y%m%d%H%M')) 
			msgNextDay =	''
			msgAlarm1 = ""
			for dictLine in dictNextAlarms:
				# clear field to create message to show
				titleAlarm = ""
				msgAlarm = ""

				# Saves alarm flags status
				flagAlarmOneDay = int(dictNextAlarms[dictLine][1])
				flagAlarmOneHour = int(dictNextAlarms[dictLine][2])
				flagAlarm30Minutes = int(dictNextAlarms[dictLine][3])
				flagAlarm15Minutes = int(dictNextAlarms[dictLine][4])
				flagAlarmExactHour = int(dictNextAlarms[dictLine][5])

				# If database has any alarm to play, play it!
				if (dictLine in [justNow, oneHourBefore, halfHourBefore, fifteenMinutesBefore] or dictLine >= tomorrowStart and dictLine <= tomorrowEnd):
					# Alarm for appointments next day
					if flagAlarmOneDay and dictLine>=tomorrowStart and dictLine<=tomorrowEnd:
						flagAlarmOneDay = False
						dictNextAlarms[dictLine][1]=0
						msgAlarm1 = _("You have the following appointment tomorrow:\n")
						msgAddHour=str(dictLine)[8:10] + ':' + str(dictLine)[10:]
						msgNextDay += msgAddHour+', '+dictNextAlarms[dictLine][0]+'\n'
						msgAlarm1 += msgNextDay

					# Alarm for appointments in an hour
					if flagAlarmOneHour and dictLine == oneHourBefore:
						flagAlarmOneHour = False
						dictNextAlarms[dictLine][2]=0
						titleAlarm = _("Reminder!")
						msgAlarm = _("You have the following appointment in one hour:\n")

					# Alarm for appointments in 30 minutes
					if flagAlarm30Minutes and dictLine == halfHourBefore:
						flagAlarm30Minutes = False
						dictNextAlarms[dictLine][3]=0
						titleAlarm = _("Reminder!")
						msgAlarm = _("You have the following appointment in 30 minutes:\n")

					# Alarm for appointments in 15 minutes
					if flagAlarm15Minutes and dictLine==fifteenMinutesBefore:
						flagAlarm15Minutes = False
						dictNextAlarms[dictLine][4]=0
						titleAlarm = _("Reminder!")
						msgAlarm = _("You have the following appointment in 15 minutes:\n")

					# Alarm for appointments now
					if flagAlarmExactHour and dictLine == justNow:
						flagAlarmExactHour = False
						dictNextAlarms[dictLine][5]=0
						titleAlarm = _("Reminder!")
						msgAlarm = _("You have now the following appointment:\n")

					# If we have a title, we have an alarm, so show the message
					if len(titleAlarm)>0:
						from . configPanel import alarmSoundToUse
						ringFile = os.path.join(os.path.dirname(__file__), "sounds", alarmSoundToUse)
						winsound.PlaySound(ringFile, winsound.SND_FILENAME|winsound.SND_ASYNC)

						dlg = wx.MessageDialog(None, msgAlarm + dictNextAlarms[dictLine][0], titleAlarm, wx.OK)
						dlg.ShowModal() 
						dlg.Destroy()
			# if flagOneDay was set
			if len(msgAlarm1) != 0:
				from . configPanel import alarmSoundToUse
				ringFile = os.path.join(os.path.dirname(__file__), "sounds", alarmSoundToUse)
				winsound.PlaySound(ringFile, winsound.SND_FILENAME|winsound.SND_ASYNC)
				dlg = wx.MessageDialog(None, msgAlarm1, _("Reminder!"), wx.OK)
				dlg.ShowModal() 
				dlg.Destroy()

# Load all alarms after now
def loadAlarms(allow):
	global flagPauseAlarm, dictNextAlarms, flagAlarmDayAfter
	allow = allow
	# Get date and time
	dateTimeNow = int(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M'))
	# Stop threadAlarme
	flagPauseAlarm=True
	# Conecting to database
	from .configPanel import dirDatabase
	what = "data, descricao, alarmedia, alarmehora, alarmemeiahora, alarmequartodehora, alarmehoraexata"
	find = "data>= " + str(dateTimeNow) + " and " + "(alarmedia or alarmehora or alarmemeiahora or alarmequartodehora or alarmehoraexata)"
	occurs = manageDatabase.findItem(what, find, dirDatabase, all=True)

	# If we have alarms scheduled, save them in dict
	dictNextAlarms = {}
	if occurs != None:
		for regLine in occurs:
			dictNextAlarms[int(regLine[0])] = list(regLine[1:])
			# Disable alert dialog if next appointments window was showed
			if not flagAlarmDayAfter:
				dictNextAlarms[int(regLine[0])][1] = 0
		flagAlarmDayAfter=True
	# load alarms from periodicity table
	alarmsFromRepeat = manageDatabase.findRepeatIntervalDate(dateTimeNow, dateTimeNow, True, dirDatabase)
	if len(alarmsFromRepeat)>0:
		for regLine in alarmsFromRepeat:
			try:
				found = regLine[4:9].index(1)
			except:
				found = -1
			# if exists alarms on periodic information
			if found!=-1:
				dictNextAlarms[int(regLine[1])] = regLine[3:9]
				# Disable alert dialog if next appointments window was showed
				if not flagAlarmDayAfter:
					dictNextAlarms[int(regLine[1])][1] = 0
		flagAlarmDayAfter=True
	flagPauseAlarm=False
	if allow == 1:
		dialog1 = nextAppointments(gui.mainFrame)
		if not dialog1.IsShown():
			gui.mainFrame.prePopup()
			dialog1.Show()
			gui.mainFrame.postPopup()
	else:
		pass


# class to store alarms
class checkBoxVars(object):
	def __init__(self):
		self.checkOneDay = False
		self.checkOneHour = False
		self.checkHalfHour = False
		self.checkFififteenMin = False
		self.checkExactTime = False

# class to store event repeat information
class eventRepeatInfo(object):
	def __init__(self):
		self.register = 0
		self.typeRepeat = -1
		self.finalDate = 0
		self.dirDatabase = ""

class generalVars(object):
	def __init__(self):
		self.titleAddEd = ''
		self.itemToEdit = 0
		self.scrollDay = None
		self.loadAlarms = False
