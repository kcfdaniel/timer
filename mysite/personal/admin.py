from django.contrib import admin
from personal.models import Game
from personal.models import Review
from personal.models import List
from personal.models import Transaction
from personal.models import Reward
from personal.models import Spending_to_next_reward

admin.site.register(Game)
admin.site.register(List)
admin.site.register(Review)
admin.site.register(Transaction)
admin.site.register(Reward)
admin.site.register(Spending_to_next_reward)