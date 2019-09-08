from urllib.request import urlretrieve

from django.shortcuts import render, redirect

from .forms import RegisterForm
from users import models
from django.shortcuts import render, redirect
from .forms import PicForm  # 上传图片的图表
from .models import Pic  # 保存上传图片相关信息的模型
from final_project.settings import MEDIA_ROOT
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
import datetime

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
				pic_name = str(timestamp) + ".JPG"
				urlretrieve(url, path + pic_name)
				picture = path + pic_name

			pic_content = models.Pic.objects.create(timestamp=timestamp, username=username, picture=picture)

		else:
			context = {}
			form = PicForm
			context['form'] = form
		return render(request, 'index.html', context)


# todo：执行前检查用户身份，用request.session
def show_pic(request, pic_id):
	try:
		pic = Pic.objects.get(pk=pic_id)
		pic_path = os.path.join('media/', str(pic.picture))

		with open(pic_path, 'rb') as image:
			image_data = image.read()
		# 使用文件流，从服务器后台发送图片（二进制数据）到网页
		return django.http.HttpResponse(image_data, content_type='image/png')  # 暂定都是png格式文件
	except Exception as e:
		print(e)
		return django.http.HttpResponse(str(e))


# 使用AJAX动态返回表单
# todo：执行前检查用户身份，用request.session
def check_records(request, page):
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


# 按照日期范围查询记录
def search(request, page):
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


def upload_and_view(request):
	return render(request, 'users/upload_and_view.html')


def delete(request, pic_id):
	try:
		# 传入False参数使得ImageField不保存文件，将其一起删除
		Pic.objects.get(pk=pic_id).delete(False)
		return

	except ObjectDoesNotExist as e:
		return django.http.HttpResponse(e)
