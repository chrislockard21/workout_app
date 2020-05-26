from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from .models import OneRepMax
from .forms import OneRepMaxForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms import modelformset_factory, inlineformset_factory
from log.models import LogHistory, SetHistory
from datetime import datetime as dt
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

# Create your views here.

class ProfileIndex(LoginRequiredMixin, View):
    template_name = 'user_profile/profile_index.html'
    form_class = OneRepMaxForm
    login_url = 'login'

    def get(self, request):
        prs = OneRepMax.objects.filter(user=request.user)
        log_history = LogHistory.objects.filter(user=request.user, created_at__range=[timezone.now()-timedelta(days=30), timezone.now()]).order_by("-created_at")
        log_set_history = {}
        for log in log_history:
            sets = SetHistory.objects.filter(user=request.user, log_history=log)
            log_set_history[log] = sets
        context = {
            'prs': prs,
            'log_set_history': log_set_history,
            'user': request.user,
            'form': self.form_class(None),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            pr = form.save(commit=False)
            pr.user = request.user
            pr.save()
            return HttpResponseRedirect(reverse('user_profile:profile_index'))
        else:
            prs = OneRepMax.objects.filter(user=request.user)
            log_history = LogHistory.objects.filter(user=request.user, created_at__range=[timezone.now()-timedelta(days=30), timezone.now()]).order_by("-created_at")
            context = {
                'prs': prs,
                'log_set_history': log_set_history,
                'user': request.user,
                'form': form,
            }
            return render(request, self.template_name, context)

class ORMEdit(LoginRequiredMixin, View):
    template_name = 'user_profile/profile_orm_edit.html'
    OneRepMaxFormset = inlineformset_factory(User, OneRepMax, form=OneRepMaxForm, extra=0)
    login_url = 'login'

    def get(self, request):
        formset = self.OneRepMaxFormset(instance=request.user)
        context = {
            'formset': formset,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        formset = self.OneRepMaxFormset(request.POST, instance=request.user)
        if formset.is_valid():
            formset.save()

            return HttpResponseRedirect(reverse('user_profile:profile_index'))
        else:
            context = {
                'formset': formset,
            }
            return render(request, self.template_name, context)

class History(LoginRequiredMixin, View):
    template_name = 'user_profile/history.html'
    login_url = 'login'

    def get(self, request):
        log_history = LogHistory.objects.filter(user=request.user).order_by("-created_at")
        log_set_history = {}
        for log in log_history:
            sets = SetHistory.objects.filter(user=request.user, log_history=log)
            log_set_history[log] = sets
        context = {
            'log_set_history': log_set_history,
        }
        return render(request, self.template_name, context)
