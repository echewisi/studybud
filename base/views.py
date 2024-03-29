from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse
from .models import Room, Topic, Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm


def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password').lower()

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username or password incorrect')
    context = {'page': page}

    return render(request, 'base/login_registration.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        "rooms": rooms,
        "topics": topics,
        'room_count': room_count,
        'room_messages': room_messages,
    }

    return render(request, 'base/home.html', context)


def room(request, pk):

    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    participants_count = room.participants.count()
    if request.method == 'POST':
        valid_message = Message.objects.create(
            user=request.user,
            room=room,
            # the 'body' here refers to value stated in the 'name' parameter of the form in the template.
            body=request.POST.get('body'),

        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'room_messages': room_messages,
            'participants': participants, 'participants_count': participants_count}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
        else:
            return redirect('create-room')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    # this is the prefilled data when the roomform is accessed
    form = RoomForm(instance=room)
    if request.user != room.host:
        # return HttpResponse('not authorized!')
        return redirect(to='room')
        

    if request.user == room.host:       
        if request.method == 'POST':
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect(to='home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('not authorized!')
    if request.method == 'POST':
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj': room})


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.password = user.password.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'password or username incorrect')
    context = {'form': form}
    return render(request, 'base/login_registration.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    room_message = Message.objects.get(id=pk)
    if request.user != room_message.user:
        return HttpResponse('you\'re not allowed here!')

    if request.method == 'POST':
        room_message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room_message})


# Create your views here.
