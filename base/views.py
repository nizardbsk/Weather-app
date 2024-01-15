from datetime import datetime
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from .models import *
from .forms import *
import json
import requests
# Create your views here.

def fetch_weather_forecast(city,api_key,current_weather_url):
    response=requests.get(current_weather_url.format(city,api_key)).json()
    # lat,lon=response['coord']['lat'],response['coord']['lon']
    # forecast_response=requests.get(forecast_url.format(lat, lon, api_key)).json()
    sunrise=datetime.utcfromtimestamp(response['sys']['sunrise']+response['timezone'])
    sunset=datetime.utcfromtimestamp(response['sys']['sunset']+response['timezone'])
    weather_data={
        'city':city,
        'temperature':round(response['main']['temp'] - 273 ,2),
        'description':response['weather'][0]['description'],
        'wind_speed':response['wind']['speed'],
        'humidity':response['main']['humidity'],
        'icon':response['weather'][0]['icon'],
        'max_temp':round(response['main']['temp_max'] - 273 ,2),
        'min_temp':round(response['main']['temp_min'] - 273 ,2),
        'feels_like':round(response['main']['feels_like']-273, 2),
        'sunrise':sunrise.strftime('%H:%M'),
        'sunset':sunset.strftime('%H:%M'),
        'pressure':response['main']['pressure']
    }
    # daily_forecasts=[]
    # for data in forecast_response['daily'][:5]:
    #     daily_forecasts.append({
    #         'day':datetime.datetime.fromtimestamp(data['dt']).strftime('%A'),
    #         'min_temp':round(data['temp']['min'] - 273 ,2),
    #         'max_temp':round(data['temp']['max'] - 273 ,2),
    #         'description':data['weather'][0]['description'],
    #         'icon':data['weather'][0]['icon']
    #     })
    return weather_data
def cities_info(profile):
    cities=[city for city in profile.cities.all()]
    api_key='1069185efa6e3bd1d8092463345d1961'
    current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    tempratures,humidities={},{}
    for c in cities:
        tempratures[c]=fetch_weather_forecast(c,api_key,current_weather_url)['temperature']
        humidities[c]=fetch_weather_forecast(c,api_key,current_weather_url)['humidity']
    return {'coldest':max(tempratures,key=lambda x : tempratures[x]),'hottest':min(tempratures,key=lambda x : tempratures[x]),'most_humid':max(humidities,key=lambda x : tempratures[x]),'least_humid':min(humidities,key=lambda x : tempratures[x])}
def home(request):
    if request.user.is_authenticated:
        q=request.GET.get('q') if request.GET.get('q') != None else ''
        now=datetime.now()
        time_now=now.strftime('%H:%M')
        user=request.user
        profile=Profile.objects.get(user=user)
        api_key='1069185efa6e3bd1d8092463345d1961'
        current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
        forecast_url='https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'
        cities=[]
        try :
            user_cities=profile.cities.filter(Q(name__icontains=q))
        except :
            user_cities=[]
        for cit in user_cities :
            cities.append({'city':cit,'weather':fetch_weather_forecast(cit,api_key,current_weather_url)})
        context={'cities':cities,'time_now':time_now,'profile':profile,'city_info':cities_info(profile)}
        return render(request,'base/home.html',context)
    else :
        pass
def addcitypage(request):
    user=request.user
    profile=Profile.objects.get(user=user)
    context={}
    if request.method == 'POST':
        city=request.POST['city']
        try:
            town=City.objects.get(name=city)
            return redirect('home')
        except:
            town=City.objects.create(
                name=city
            )
            profile.cities.add(town)
            profile.save()
            return redirect('home')
    return render(request,'base/add_city.html',context)

def comparison_logic(city1,city2):
    api_key='1069185efa6e3bd1d8092463345d1961'
    current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url='https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'
    city1_weather=fetch_weather_forecast(city1,api_key,current_weather_url)
    city2_weather=fetch_weather_forecast(city2,api_key,current_weather_url)
    if city1_weather['temperature']>city2_weather['temperature']:
        colder=city2
        cold=city1_weather['temperature']-city2_weather['temperature']
    else :
        colder=city1
        cold=city2_weather['temperature']-city1_weather['temperature']
    if city1_weather['humidity']>city2_weather['humidity']:
        humid=city1
        more_humid=city1_weather['humidity']/city2_weather['humidity']
    else:
        humid=city2
        more_humid=city2_weather['humidity']/city1_weather['humidity']
    if city1_weather['wind_speed']>city2_weather['wind_speed']:
        faster=city1
        fast=city1_weather['wind_speed']/city2_weather['wind_speed']
    else:
        faster=city2
        fast=city2_weather['wind_speed']/city1_weather['wind_speed']
    return {'colder':colder,'humid':humid,'faster':faster,'cold':round(cold,2),'more_humid':round(more_humid,2),'fast':round(fast,2)}

def compare(request):
    one_comparison=False
    api_key='1069185efa6e3bd1d8092463345d1961'
    profile=request.user.profile
    current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url='https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'
    now=datetime.now()
    time_now=now.strftime('%H:%M')
    text=False
    context={}
    
    if request.method == 'POST':
        city1,created=City.objects.get_or_create(name=request.POST['city1'])
        city2,created=City.objects.get_or_create(name=request.POST['city2'])
        text=True
        compare_cities,cities=[city1,city2],[]
        for city in compare_cities:
            cities.append({'city':city,'weather':fetch_weather_forecast(city,api_key,current_weather_url)})
        context['cities']=cities
        context['comparison']=comparison_logic(city1,city2)
    context['time_now']=time_now
    context['text']=text
    context['profile']=profile
    context['one_comparison']=one_comparison
    return render(request,'base\comparison_page.html',context)
def citypage(request,city_id):
    api_key='1069185efa6e3bd1d8092463345d1961'
    profile=request.user.profile
    current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url='https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'
    place=City.objects.get(id=city_id)
    time_now=datetime.now()
    context={'weather':fetch_weather_forecast(place,api_key,current_weather_url),'city':place,'profile':profile,'time_now':time_now}
    if request.method=='POST':
        city1_id=city_id
        city2,created=City.objects.get_or_create(name=request.POST.get('comparison-input'))
        city2_id=city2.id
        return redirect('compare-with',city1_id,city2_id)
    return render(request,'base\city-page.html',context)

def profilepage(request,profile_id):
    context={'profile':Profile.objects.get(id=profile_id)}
    return render(request,'base\profile-page.html',context)
def updateprofile(request,profile_id):
    profile=Profile.objects.get(id=profile_id)
    form=ProfileUpdateForm(instance=profile)
    if request.method == 'POST':
        form=ProfileUpdateForm(request.POST,request.FILES,instance=profile)
        if form.is_valid:
            form.save()
            return redirect('profile-page',profile.id)
    context={'form':form,'profile':profile}
    return render(request,'base\profile-update.html',context)

def comparewith(request,city1_id,city2_id):
    one_comparison=True
    api_key='1069185efa6e3bd1d8092463345d1961'
    current_weather_url='https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    forecast_url='https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'
    text=True
    now=datetime.now()
    time_now=now.strftime('%H:%M')
    city1=City.objects.get(id=city1_id)
    city2=City.objects.get(id=city2_id)
    print('CITY1 : ',city1,'----','CITY2 : ',city2)
    profile=request.user.profile
    context={}
    compare_cities,cities=[city1,city2],[]
    for city in compare_cities:
        cities.append({'city':city,'weather':fetch_weather_forecast(city,api_key,current_weather_url)})
    context['cities']=cities
    context['comparison']=comparison_logic(city1,city2)
    context['time_now']=time_now
    context['text']=text
    context['profile']=profile
    context['one_comparison']=one_comparison
    return render(request,'base\comparison_page.html',context)
