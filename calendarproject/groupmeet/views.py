from django.shortcuts import render, redirect,  get_object_or_404
from .models import User, Schedule, Group, GroupSchedule
import datetime
import calendar
from .calendar import Calendar
from django.utils.safestring import mark_safe
import logging

#Calendar: 한달 단위 모든 일정
#Schedule: 일정 하나 하나

# Create your views here.

def userCalendar_view(request):
   return render(request, 'userCalendar.html')

#사용자의 Id를 받아와서 사용자가 속한 group list return
def getuserGroupList(request,id):
   user = get_object_or_404(User, userId=id)
   userGroup_list=list(user.groups.all())  #userid를 받아와서 user가 속한 usergroup 부르기
   return render(request,'userGroupList.html',{'userGroup_list':userGroup_list})

# 그룹 캘린더 보여주기
def groupCalendar_view(request, id):            
   today = get_date(request.GET.get('month'))
   prev_month_url = prev_month(today)
   next_month_url = next_month(today)
   cur_month_url = "month=" + str(today.year) + '-' + str(today.month)
   # now = datetime.now()
   # cur_year = now.year        # 현재 연도
   # cur_month = now.month      # 현재 월
   group = Group.objects.get(id=id)
   cal = Calendar(today.year, today.month)
   cal = cal.formatmonth(withyear=True, group=group)
   cal = mark_safe(cal)

   #group에 속한 user들의 모든 일정 list로 return
   if request.GET.get('day'):
      day = request.GET.get('day')
   else:
      day = today.day
   schedule_list={9:[0,0], 10:[0,0], 11:[0,0], 12:[0,0], 13:[0,0], 14:[0,0], 15:[0,0], 16:[0,0], 17:[0,0], 18:[0,0], 19:[0,0], 20:[0,0], 21:[0,0]}
   members= group.members.all()
   date_format = str(today.year)+"-"+str(today.month).zfill(2)+"-"+str(day).zfill(2)
   for user in members:
      schedules = Schedule.objects.filter(user=user, start__lte = date_format+" 22:00:00", end__gte = date_format+" 09:00:00")
      if schedules:
         for schedule in schedules:
            if schedule.start < datetime.datetime(int(today.year), int(today.month), int(day), 9, 0):
               s = 9
            else:
               if schedule.start.minute == 30:
                  schedule_list[schedule.start.hour][1] = 1
               s = schedule.start.hour + 1 if schedule.start.minute == 30 else int(schedule.start.hour)
            if schedule.end > datetime.datetime(int(today.year), int(today.month), int(day), 22, 0):
               e = 21
            else:
               if schedule.end.minute == 30:
                  schedule_list[schedule.end.hour][0] = 1
               e = schedule.end.hour - 1
            for i in range(s, e+1):
               schedule_list[i][0] = 1
               schedule_list[i][1] = 1
   groupschedules = GroupSchedule.objects.filter(group=group, start__year=today.year, start__month=today.month, start__day=day)
   return render(request, 'groupCalendar.html', {'groupschedules':groupschedules,'calendar' : cal, 'cur_month' : cur_month_url, 'prev_month' : prev_month_url, 'next_month' : next_month_url, 'groupId' : id,'schedule_list':schedule_list, 'date' : [today.year, str(today.month).zfill(2), str(day).zfill(2)]})
def get_date(request_day):
   if request_day:
      year, month = (int(x) for x in request_day.split('-'))
      return datetime.date(year, month, day=1)
   return datetime.datetime.today()

def prev_month(day):                                                          # 이전 달에 해당하는 URL 리턴
   first = day.replace(day=1)                                                 # first = today가 있는 달의 첫번째 날이 됨
   prev_month = first - datetime.timedelta(days=1)                            # prev_month = 첫 번째 날에서 하루를 뺌, 즉 저번 달 말일이 됨
   month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
   return month

def next_month(day):                                                          # 다음 달에 해당하는 URL 리턴
   days_in_month = calendar.monthrange(day.year, day.month)[1]
   last = day.replace(day=days_in_month)                                      # last = today가 있는 달의 마지막 날이 됨
   next_month = last + datetime.timedelta(days=1)                             # next_month = today에서 하루가 더 해진 날, 즉 다음 달 1일이 됨
   month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
   return month

def createGroupSchedule(request, group_id):
   newGroupSchedule = GroupSchedule()
   newGroupSchedule.group = Group.objects.get(pk=group_id)
   newGroupSchedule.start =  request.POST.get('start') # 날짜/시간 프론트에서 어떻게 받는지에 따라 수정
   newGroupSchedule.end =  request.POST.get('end') # 날짜/시간 프론트에서 어떻게 받는지에 따라 수정
   newGroupSchedule.title =  request.POST.get('title')
   newGroupSchedule.save()
   return redirect('groupCalendar', group_id)

def allowRegister(request, groupSchedule_id):
   groupSchedule = GroupSchedule.objects.get(pk = groupSchedule_id)
   newUserSchedule = Schedule()
   newUserSchedule.user = request.session.get('user')
   newUserSchedule.start =  groupSchedule.start
   newUserSchedule.end = groupSchedule.end
   newUserSchedule.title = groupSchedule.title
   newUserSchedule.save()
   return redirect('groupCalendar', groupSchedule.group) # group id를 인자로 (group_id/group)
