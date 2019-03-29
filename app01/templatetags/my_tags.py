#! -*- coding:utf-8 -*-
from django import template
from django.db.models import Count
from app01.models import UserInfo,Article,Category,Tag
from  django.db.models.functions import TruncMonth


register=template.Library()

@register.inclusion_tag("classification.html")
def get_classification_style(username):

    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title","c")
    tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")
    date_list = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(
        c=Count("nid")).values_list("month", "c")

    return {"blog":blog,"cate_list":cate_list,"date_list":date_list,"tag_list":tag_list,"user":user}
