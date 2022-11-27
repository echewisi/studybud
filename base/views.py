from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q


def loginpage(request):
    return render(request, 'base/login_registration.html')

def home(request):
    q= request.GET.get('q') if request.GET.get('q')!= None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        )
    topics= Topic.objects.all() 
    room_count=rooms.count()
    context={
        "rooms":rooms,
        "topics":topics,
        'room_count':room_count
    }
    
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}
    return render(request, 'base/room.html', context)


def create_room(request):
    form = RoomForm
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('home')
        else:
            return redirect('create-room')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
    room= Room.objects.get(id=pk)
    form= RoomForm(instance= room) #this is the prefilled data when the roomform is accessed
    if request.method== 'POST':
        form= RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect( to='home')
    context={'form':form}
    return render(request, 'base/room_form.html', context) 

def deleteRoom(request, pk):
    room= Room.objects.get(id=pk)
    if request.method== 'POST':
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})
# Create your views here.
