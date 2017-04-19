from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from personal.models import Game
#from personal.models import Tag
from personal.models import List
from personal.models import Transaction
from personal.models import Reward
from personal.models import Spending_to_next_reward
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal


def hello(request):
	review_text = request.POST.get("r")
	if review_text:
		return render(request,'personal/basic.html', {'content':[review_text]})
	else:
		return render(request,'personal/basic.html', {'content':[review_text]})

def index(request):
	return render(request,'personal/home.html')

def contact(request):
	return render(request,'personal/basic.html', {'content':['If you would like to cocntact me','kcfdaniel@gmail.com']})

def game(request):
	return render(request,'personal/game.html')

##In the current implementation, the title works only if there is at least a game in that genre
def genre(request):
	search_result=[]
	genre=request.path.split('/')[2].capitalize()
	for game in Game.objects.all():
		if game.genre.lower() == genre.lower():
			genre=game.genre
			search_result.append(game)
	return render(request,'personal/genre.html',{'content':[Game.objects.all(),search_result,genre]})


def home(request):
	featured_list=[]
	recently_purchase=[] #last 3 purchase
	recommended_list=[]
	purchased_game_id=[]

	#Get featured list
	id_list=List.objects.filter(name='Featured List').values_list('games', flat=True)
	for i in id_list:
		featured_list.append(Game.objects.get(pk=i))

	if request.user.is_authenticated():
		#Get recommended list
		purchase_history = Transaction.objects.filter(buyer=request.user).order_by('-date')

		for i in purchase_history.values_list('game', flat=True):
			purchased_game_id.append(i)

		recently_purchase = purchase_history[:3]


		for i in recently_purchase:
			similar_games = i.game.tag.similar_objects()
			for g in similar_games:
				if not Transaction.objects.filter(buyer=request.user, game=g).exists() and g not in recommended_list:
					recommended_list.append(g)
					break
			#recommended_list.append(g.tag.similar_objects()[0])
		return render(request,'personal/home.html',{'content':[Game.objects.all(),featured_list, recommended_list, recently_purchase, purchase_history]})
	else:
		return render(request,'personal/home.html',{'content':[Game.objects.all(),featured_list]})


def search(request):
	search_result=Game.objects.all()
	if request.user.is_staff or request.user.is_superuser:
		search_result = Game.objects.all()

	query = request.GET.get("q")
	if query:
		search_result = search_result.filter(
			Q(tag__name__icontains=query)
			)

	##search_result=[]
	##search_result.append(Game.objects.filter(tag__name=query))
	return render(request,'personal/search.html',{'content':[search_result,query,Game.objects.all()]})

@login_required
def add_tag(request, game_id):

	tag_name = request.POST.get("t")
	if tag_name:
		g = Game.objects.get(id=game_id)
		if (Transaction.objects.filter(buyer=request.user,game=g).exists()):
			g.tag.add(tag_name)
		else:
			messages.error(request, "You have to purchase the game to add tags.")

	return HttpResponseRedirect('/game/'+game_id)

@login_required
def add_review(request, game_id):
	review_text = request.POST.get("r")
	if review_text:
		now = datetime.now()
		g = Game.objects.get(id=game_id)
		if (Transaction.objects.filter(buyer=request.user,game=g).exists()):
			g.review_set.create(text=review_text, date=now, game=game_id, writer=request.user)
		else:
			messages.error(request, "You have to purchase the game to add reviews.")
	return HttpResponseRedirect('/game/'+game_id)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def select_reward(request, game_id):
	#check if any rewards expired
	for reward in Reward.objects.filter(user=request.user):
		if reward.expiry_date < timezone.now():
			reward.delete()


	g = Game.objects.get(id=game_id)
	if not Transaction.objects.filter(buyer=request.user, game=g):
		rewards=Reward.objects.filter(user=request.user)



		featured_list=[]
		id_list=List.objects.filter(name='Featured List').values_list('games', flat=True)
		for i in id_list:
			featured_list.append(Game.objects.get(pk=i))
		return render(request, 'personal/select_reward.html', {'content':[Game.objects.all(),featured_list,rewards,game_id]})
	else:
		messages.error(request, "You have already purchased the game!")
		return HttpResponseRedirect('/game/'+game_id)

def confirm_purchase(request, game_id):
	g = Game.objects.get(id=game_id)

	if not request.POST.get('r'):
		number_of_rewards = 0
	else:
		number_of_rewards = int(request.POST.get('r'))

	money_going_to_pay = g.price*(10-number_of_rewards)/10

	request.session['number_of_rewards']=str(number_of_rewards)
	request.session['money_going_to_pay']=str(money_going_to_pay)
	return render(request, 'personal/confirm_purchase.html', {'content':[Game.objects.all(),g,number_of_rewards,money_going_to_pay,game_id]})

def confirmed(request, game_id):
	if 'confirm' in request.POST:
		number_of_rewards=int(request.session['number_of_rewards'])
		money_going_to_pay=Decimal(request.session['money_going_to_pay'])
		g = Game.objects.get(id=game_id)
		request.user.spending_to_next_reward.amount-=money_going_to_pay

		if request.user.spending_to_next_reward.amount <= 0:
			request.user.spending_to_next_reward.amount+=100
			request.user.save()
			Reward.objects.create(user=request.user)

		for i in range(0,number_of_rewards):
			Reward.objects.filter(user=request.user)[0].delete()


		request.user.save()

		now = datetime.now()
		Transaction.objects.create(buyer=request.user, game=g, date=now)
		messages.success(request, "Successfully Purchased the game!")
	elif 'cancel' in request.POST:
		messages.error(request, "Purchase canceled!")
	return HttpResponseRedirect('/game/'+game_id)
