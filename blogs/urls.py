"""blogs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,re_path
from django.views.static import serve
from app01 import views
from blogs import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path("^$",views.index),
    path('login/',views.login,name="login"),
    path('get_validCode_img',views.get_validCode_img,name="validCode"),
    path("index/",views.index),
    path('register/',views.register,name='register'),
    path('logout/',views.logout,name="logout"),
    # 后台管理
    re_path("cn_backend/$", views.cn_backend),
    re_path("cn_backend/add_article/$", views.add_article),
    re_path('cn_backend/article/(\d+)/remove/',views.remove_article),
    re_path('cn_backend/article/(\d+)/change/',views.change_article,name="change_article"),

    # 文本编辑器上传图片url
    path('upload/', views.upload),
    # 文章点赞
    path("digg/",views.digg),
    # 文章评论路由
    path("comment/",views.comment),
    # media 配置
    re_path(r"media/(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),
    # 个人站点url配置
    re_path("^(?P<username>\w+)/$",views.home_site),
    # 个人站点跳转url配置
    re_path("^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/",views.home_site),
    # 文章详情页
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)/$', views.article_detail),


]
