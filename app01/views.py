from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import auth
from app01.utils.validCode import validCode_img
from app01.Myform import UserForm
from app01.models import UserInfo, Article, Category, Tag, ArticleUpDown, Comment
from django.db.models import F
from django.db import transaction
from blogs import settings
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json, os


# Create your views here.


# 首页部分
def login(request):
    """用户登录验证视图"""
    if request.method == "POST":
        response = {"user": None, "msg": None}
        username = request.POST.get("username")
        password = request.POST.get("password")
        valid_code = request.POST.get("valid_code")
        valid_code_str = request.session.get("valid_code_str")
        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                response["user"] = user.username
            else:
                response['msg'] = "用户名或密码输入错误！"
        else:
            response["msg"] = "验证码输入错误!"
        return JsonResponse(response)
    return render(request, 'login.html')


def get_validCode_img(request):
    """生成验证码图片"""
    Code_img = validCode_img(request)
    return HttpResponse(Code_img)


def register(request):
    """用户注册视图"""
    if request.is_ajax():
        form = UserForm(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("username")
            # 生成记录
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            avatar_obj = request.FILES.get("avatar")
            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj
            UserInfo.objects.create_user(username=username, email=email, password=password, **extra)
        else:
            response["msg"] = form.errors

        return JsonResponse(response)
    form = UserForm()
    return render(request, 'register.html', {"form": form})


def logout(request):
    """用户注销视图"""
    auth.logout(request)
    return redirect("/login/")



def index(request):
    """首页视图"""
    article_list = Article.objects.all()
    # 分页器
    paginator = Paginator(article_list, 5)
    current_page_num = int(request.GET.get("page",1))
    if paginator.num_pages > 11:
        if current_page_num - 5 < 1:
            page_range = range(1, 12)
        elif current_page_num + 5 > paginator.num_pages:
            page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
        else:
            page_range = range(current_page_num - 5, current_page_num + 6)
    else:
        page_range = paginator.page_range

    try:
        current_page = paginator.page(current_page_num)

    except EmptyPage as e:
        current_page = paginator.page(1)

    return render(request, 'index.html', locals())


# 个人站点部分
def home_site(request, username, **kwargs):
    """
    个人站点视图函数
    :param request:
    :param username:
    :param kwargs:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "404.html")
    # 当前站点
    blog = user.blog
    # 当前用户及当前站点的所有文章
    # 基于对象
    # article_list = user.article_set.all()
    # 基于双下滑线 跨表
    article_list = Article.objects.filter(user=user)
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "category":
            article_list = article_list.filter(category__title=param)

        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    paginator = Paginator(article_list, 4)
    current_page_num = int(request.GET.get("page", 1))
    if paginator.num_pages > 11:
        if current_page_num - 5 < 1:
            page_range = range(1, 12)
        elif current_page_num + 5 > paginator.num_pages:
            page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
        else:
            page_range = range(current_page_num - 5, current_page_num + 6)
    else:
        page_range = paginator.page_range

    try:
        current_page = paginator.page(current_page_num)
    except EmptyPage as e:
        current_page = paginator.page(1)

    return render(request, 'home_site.html', locals())


def article_detail(request, username, article_id):
    """
    文章详情页 视图函数
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())


# 文章操作部分
def digg(request):
    """文章点赞视图"""
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))  # "true"
    # 点赞人即当前登录人
    user_id = request.user.pk
    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"state": True}
    if not obj:
        ard = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)

        queryset = Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = obj.is_up

    return JsonResponse(response)


def comment(request):
    """文章评论视图"""
    # print(request.POST)

    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk
    article_obj = Article.objects.filter(pk=article_id).first()
    # 防止xss攻击,过滤script标签
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.find_all():
        if tag.name == "script":
            tag.decompose()
    # 添加记录
    # comment_obj = Comment.objects.create(user_id=user_id,article_id=article_id,content=content,parent_comment_id=pid)
    with transaction.atomic():
        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)
    response = {}
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d-%X")
    response["username"] = comment_obj.user.username
    response["content"] = content


    return JsonResponse(response)


# 后台管理
@login_required
def cn_backend(request):
    """
    后台管理的首页
    :param request:
    :return:
    """
    article_list = Article.objects.filter(user=request.user)

    return render(request, "backend/backend.html", locals())


@login_required
def add_article(request):
    """
    后台管理的添加书籍视图函数
    :param request:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            print(tag.name)
            if tag.name == "script":
                tag.decompose()

        # 构建摘要数据,获取标签字符串的文本前150个符号

        desc = soup.text[0:150] + "..."

        Article.objects.create(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/add_article.html")


@login_required
def remove_article(request, remove_article_id):
    """删除文章视图"""
    print(remove_article_id)

    Article.objects.filter(pk=remove_article_id).delete()
    return redirect("/cn_backend/")

@login_required
def change_article(request,article_id):
    """
    文章编辑视图
    :param request:
    :param article_id:
    :return:
    """
    change_article = Article.objects.filter(pk=article_id).first()
    if  request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        Article.objects.filter(pk=article_id).update(title=title,content=content)
        return redirect("/cn_backend/")

    return render(request,"backend/change_article.html",locals())





def upload(request):
    """
    编辑器上传文件接受视图函数
    :param request:
    :return:
    """
    img_obj = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)
    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)

    response = {
        "error": 0,
        "url": "/media/add_article_img/%s" % img_obj.name
    }
    return HttpResponse(json.dumps(response))
