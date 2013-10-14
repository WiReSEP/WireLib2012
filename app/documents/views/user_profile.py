# vim: set fileencoding=utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from documents.forms import NameForm
from documents.models import Document, TelUser
from lib_views import _get_dict_response


def profile_edit_name(request):
    """
    Methode zum Ändern des eigenen Namens
    """
    v_user = request.user
    if request.method == "POST":
        form = NameForm(request.POST, instance=v_user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("profile.edit.personal.done"))
    else:
        form = NameForm(instance=v_user)
        template = "profile/name.html"
        data = {'form': form, }
        return render_to_response(template, data,
                                  context_instance=RequestContext(request))


def telpersonal(request):
    """Bearbeitung der Mail-Adresse
    """

    telformset = modelformset_factory(TelUser, extra=3, max_num=3,
                                      can_delete=True, exclude='user')
    query = TelUser.objects.filter(user=request.user)
    if request.method == "POST":
        formset = telformset(request.POST, queryset=query)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
            return HttpResponseRedirect(reverse("profile.edit.personal.done"))
    else:
        formset = telformset(queryset=query)
    template = "profile/tel.html"
    data = {'formset': formset, }
    return render_to_response(template, data,
                              context_instance=RequestContext(request))


@login_required
def profile(request, user_id=None):
    """View der Profilübersicht
    """
    v_user = request.user
    if user_id:
        try:
            p_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
    else:
        p_user = v_user
    see_groups = v_user.has_perm('documents.can_see_others_groups')
    miss_query = Document.objects.filter(docstatus__status=Document.MISSING,
                                         docstatus__return_lend=False)
    miss_query = miss_query.order_by('-docstatus__date')
    dict_response = _get_dict_response(request)
    if p_user.id == v_user.id:
        context = Context(dict_response)
        return render_to_response("profile.html", context_instance=context)
    dict_response["p_user"] = p_user
    dict_response["see_groups"] = see_groups
    context = RequestContext(request, dict_response)
    return render_to_response("stranger_profile.html",
                              context_instance=context)


@login_required
def profile_settings(request, user_id=None):
    """View der Accounteinstellung
    """
    v_user = request.user
    if user_id:
        c_user = User.objects.get(id=user_id)
        if not v_user == c_user:
            # test rights to edit other users
            raise PermissionDenied
    else:
        c_user = v_user
    dict_response = _get_dict_response(request)
    dict_response["c_user"] = c_user
    context = RequestContext(request, dict_response)
    return render_to_response("profile_settings.html", context_instance=context)
