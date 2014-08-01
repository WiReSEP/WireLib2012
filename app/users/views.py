from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from users import models
from users import forms


class UserEdit(generic.edit.UpdateView):
    model = models.User
    template_name = "users/edit.html"
    form_class = forms.UserEditForm

    def get_object(self):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserEdit, self).dispatch(*args, **kwargs)


class UserProfile(generic.DetailView):
    model = models.User
    template_name = "users/detail.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'
