from django.shortcuts import render
from personal.models import Game
from personal.models import Reward
from django.contrib.auth.models import User
from django import template

register=template.Library()

@register.inclusion_tag('personal/navigation.html')
def navigation(selected_id=None):
    return {
        'navigation': Game.objects.all(),
        'selected':selected_id,
    }

@register.inclusion_tag('personal/reward_navigation.html')
def reward_navigation(u, selected_id=None):

    return {
        'reward_navigation': Reward.objects.filter(user=u).order_by('-issue_date'),
        'selected':selected_id,
    }