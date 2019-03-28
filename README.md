# Ee3Blog.V1
第一个Django项目博客系统雏形
## 开发环境

- **Python3.6.5**
- **Django2.1.7**
- **MySQL5.6.42**

## 迁移表

```
python3 manage.py  makemigrations
python3 manage.py  migrate
```

## 依赖环境

- bs4模块：xss防御，文章摘要
- pillow模块：图片验证码

## 错误信息

#### 0x1-迁移表错误信息

```
ERRORS:
app01.UserInfo.groups: (fields.E304) Reverse accessor for 'UserInfo.groups' clashes with reverse accessor for 'User.groups'.
        HINT: Add or change a related_name argument to the definition for 'UserInfo.groups' or 'User.groups'.
app01.UserInfo.user_permissions: (fields.E304) Reverse accessor for 'UserInfo.user_permissions' clashes with reverse accessor for 'User.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'UserInfo.user_permissions' or 'User.user_permissions'.
auth.User.groups: (fields.E304) Reverse accessor for 'User.groups' clashes with reverse accessor for 'UserInfo.groups'.
        HINT: Add or change a related_name argument to the definition for 'User.groups' or 'UserInfo.groups'.
auth.User.user_permissions: (fields.E304) Reverse accessor for 'User.user_permissions' clashes with reverse accessor for 'UserInfo.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'User.user_permissions' or 'UserInfo.user_permissions'.

```

0x-2：错误信息

分页：

```
UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'app01.models.Article'> QuerySet.
```



## 解决

#### 0x1-settings.py文件

```
AUTH_USER_MODEL="app01.UserInfo"
```

0x2- 要查询的模型中加入以下内容.

```
    class Meta:
        ordering = ['nid']
```

## 创建用户

python3 manage.py createsuperuser


## 说明
这个只是学习的练手项目功能会逐步完善的，谢谢
