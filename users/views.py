from urllib.request import urlretrieve

from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext

from .forms import RegisterForm, UserForm
from users import models
from django.shortcuts import render, redirect
from .forms import PicForm  # 上传图片的图表
from .models import Pic, User  # 保存上传图片相关信息的模型
from final_project.settings import MEDIA_ROOT
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
import datetime
from users.Object_Detection import func
from users.Classification import classify_image

import django.http
import json
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


class UserFormLogin(object):
	pass


def login(request):
	if request.method == 'POST':
		userform = UserForm(request.POST)
		if userform.is_valid():
			# 获取表单用户密码
			username = userform.cleaned_data['username']
			password = userform.cleaned_data['password']
			# 获取的表单数据与数据库进行比较
			user = auth.authenticate(username=username, password=password)
			request.session["has_login"] = True
			if user:
				auth.login(request, user)
				response = HttpResponseRedirect('/')
				response.set_cookie('username', username)
				return response
			else:
				return HttpResponseRedirect('/users/login/')
	else:
		userform = UserForm()
	return render(request, 'users/login.html', {'userform': userform})


# todo：执行前检查用户身份，用request.session
def show_pic(request, pic_id):
	if request.session.get("has_login", False):
		try:
			pic = Pic.objects.get(pk=pic_id)
			pic_path = os.path.join('media/', str(pic.picture))

			with open(pic_path, 'rb') as image:
				image_data = image.read()
			# 使用文件流，从服务器后台发送图片（二进制数据）到网页
			return django.http.HttpResponse(image_data, content_type='image/png')
		except Exception as e:
			print(e)
			return django.http.HttpResponse(str(e))
	else:
		print("please login with your own session")


# 展示id对应图片的处理结果
def show_result(request, pic_id):
	if request.session.get("has_login", False):
		try:
			pic = Pic.objects.get(pk=pic_id)
			res_path = os.path.join("media/" + str(pic.res))
			print(res_path)
			while not os.path.exists(res_path):
				# 每隔0.1秒检查一次输出文件是否存在，若已输出则返回相应结果
				time.sleep(0.1)
			print('test2')
			with open(res_path, 'rb') as image:
				image_data = image.read()
			# 使用文件流，从服务器后台发送处理结果（二进制数据）到网页
			return django.http.HttpResponse(image_data, content_type='image/png')
		except Exception as e:

			print(e)
			return django.http.HttpResponse(str(e))
	else:
		print("please login with your own session")


# 使用AJAX动态返回表单
def check_records(request, page):
	if request.session.get("has_login", False):
		record_list = []
		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				record_list.append({
					'user': record.username,
					'record_id': record.id,
					'input_picture': str(record.picture),
					'output_picture': str(record.res),
					'upload_time': record.timestamp
				})

		# 规定每页10条数据，进行分割
		paginator = Paginator(record_list, 10)

		if request.method == 'GET':
			try:
				records = paginator.page(page)
			except PageNotAnInteger:
				# 如果请求的页数不是整数，返回第一页
				records = paginator.page(1)
			except EmptyPage:
				# 如果页数不在合法范围内，返回结果最后一页
				records = paginator.page(paginator.num_pages)
			except InvalidPage:
				# 如果请求的页数不存在，重定向页面
				return django.http.HttpResponse('找不到页面内容')

			template_view = 'users/check_record.html'

			return render(request, template_view, {'records': records})
	else:
		print("please login with your own session")


# 按照日期范围查询记录
def search(request, page):
	if request.session.get("has_login", False):
		start_date_str = request.GET.get('start_date')
		end_date_str = request.GET.get('end_date')
		start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
		end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

		record_list = []
		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				update_date = datetime.datetime.strptime(record.timestamp, '%Y-%m-%d %H:%M:%S').date()
				if start_date <= update_date <= end_date:
					record_list.append({
						'user': record.username,
						'record_id': record.id,
						'input_picture': str(record.picture),
						'output_picture': str(record.res),
						'upload_time': record.timestamp
					})

		# 规定每页10条数据，进行分割
		paginator = Paginator(record_list, 10)

		try:
			records = paginator.page(page)
		except PageNotAnInteger:
			# 如果请求的页数不是整数，返回第一页
			records = paginator.page(1)
		except EmptyPage:
			# 如果页数不在合法范围内，返回结果最后一页
			records = paginator.page(paginator.num_pages)
		except InvalidPage:
			# 如果请求的页数不存在，重定向页面
			return django.http.HttpResponse('找不到页面内容')

		return render(request, 'users/check_record.html',
		              {'records': records, 'searched': True, 'start_date': start_date_str, 'end_date': end_date_str})
	else:
		print("please login with your own session")


# empty file and url will make it buggy
def upload_and_view(request):
	if request.session.get("has_login", False):
		if request.method == "POST":
			form = PicForm(request.POST, request.FILES)

			if form.is_valid():
				try:
					pic = form.cleaned_data["picture"]
					url = form.cleaned_data["url"]

					current_user = request.user
					username = current_user.username

					time_now = int(time.time())
					time_local = time.localtime(time_now)
					timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
					nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
					context = {}
					form = PicForm
					context['form'] = form

					if pic:
						picture = pic
						print(type(picture))
						target_path = "media/pictures/" + picture.name
						context['classification'] = classify_image(picture)

					elif url:
						path = "./media/pictures/"
						pic_name = str(nowTime) + ".jpg"
						urlretrieve(url, path + pic_name)
						# pic_content = Pic.objects.create(timestamp=timestamp, username=username)
						picture = "pictures/" + pic_name
						target_path = "media/pictures/" + pic_name
						context['classification'] = classify_image("media/" + picture)
					# print(picture)

					pic_content = models.Pic.objects.create(timestamp=timestamp, username=username, picture=picture)

					res = func(target_path)
					res = "pictures/" + res.split("/")[-1]
					pic_content.res = res
					pic_content.save()
					context['pic_id'] = pic_content.id
					context['uploaded'] = True

				except Exception as e:
					print(e)
					return render(request, 'index.html')  # 如果没有上传照片，返回首页

			else:
				return render(request, 'index.html')  # 如果没有上传照片，返回首页

		else:
			context = {}
			form = PicForm
			context['form'] = form
	else:
		print("please login with your own session")
	return render(request, 'users/upload_and_view.html', context)


def delete(request, pic_id):
	if request.session.get("has_login", False):
		try:
			# 不保存关联的图像文件，将其一起删除
			Pic.objects.get(id=pic_id).delete()
			return check_records(request, 1)

		except ObjectDoesNotExist as e:
			return django.http.HttpResponse(e)
	else:
		print("please login with your own session")


def delete_batch(request):
	if request.session.get("has_login", False):
		start_date_str = request.POST.get('start_date')
		end_date_str = request.POST.get('end_date')
		start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
		end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

		user = request.user
		for record in Pic.objects.all():
			if record.username == user.username:
				update_date = datetime.datetime.strptime(record.timestamp, '%Y-%m-%d %H:%M:%S').date()
				if start_date <= update_date <= end_date:
					record.delete()
	else:
		print("please login with your own session")
	return django.http.HttpResponse('批量删除成功！')
