from urllib.request import urlretrieve

from django.shortcuts import render, redirect

from .forms import RegisterForm
from users import models
from django.shortcuts import render, redirect
from .forms import PicForm  # 上传图片的图表
from .models import Pic  # 保存上传图片相关信息的模型
from final_project.settings import MEDIA_ROOT

import django.http
import time
import os


def register(request):
	# get the "next" parameter from POST or GET
	# GET: "next" is passed by url -> /?next=value
	# POST: "next" is passed by form -> <input type="hidden" name="next" value="{{ next }}"/>
	# "next" will record the previous visiting page, and then redirect back after registration
	redirect_to = request.POST.get('next', request.GET.get('next', ''))

	if request.method == 'POST':
		# submit username and password
		# 實例化一個用戶註冊表單
		form = RegisterForm(request.POST)

		if form.is_valid():
			# if the form is valid, save it
			# django 自己的包
			form.save()

			if redirect_to:
				return redirect(redirect_to)
			else:
				return redirect('/')
	else:
		# if request is not POST, it indicates that the user is visiting register page.
		# so show an empty register form
		form = RegisterForm()

	return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})


def index(request):
	context = {}
	form = PicForm
	context['form'] = form
	return render(request, 'index.html', context)


def save_pic(request):
	if request.method == "POST":
		form = PicForm(request.POST, request.FILES)

		if form.is_valid():
			pic = form.cleaned_data["picture"]
			url = form.cleaned_data["url"]

			current_user = request.user
			username = current_user.username

			time_now = int(time.time())
			time_local = time.localtime(time_now)
			timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

			if pic:
				picture = pic
			elif url:
				path = "./media/pictures/"
				pic_name = str(timestamp)+".JPG"
				urlretrieve(url, path+pic_name)
				picture = path+pic_name

			pic_content = models.Pic.objects.create(timestamp=timestamp, username=username, picture=picture)

		else:
			form = PicForm()

		return render(request, 'index.html')


def show_pic(request, pic_id):
	try:
		pic = Pic.objects.get(pk=pic_id)
		pic_path = os.path.join('media/', str(pic.picture))

		with open(pic_path, 'rb') as image:
			image_data = image.read()
		# 使用文件流，从服务器后台发送图片（二进制数据）到网页
		return django.http.HttpResponse(image_data, content_type='image/png')   # 暂定都是png格式文件
	except Exception as e:
		print(e)
		return django.http.HttpResponse(str(e))
