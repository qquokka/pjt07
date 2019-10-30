---
typora-root-url: ./
typora-copy-images-to: ./
---

# Project 07: Easy Mean

##	Pair Programming을 통해 느낀점

1. 지민이는 따옴표를 쓸 때 작은 따옴표를 쓴다.
2. 혼자 할 때보다 왠지 모르게 더 피로해진다.
3. Navigator일 때는 머리가 잘 돌아가는데 키보드만 잡으면 머리가 안 돌아간다.

## 프로젝트 요약

1. 처음 http://127.0.0.1:8000/로 들어갈 때 http://127.0.0.1:8000/movies/로 들어갈 수 있도록 easy_mean/urls.py 안에 함수 go_homepage를 만들었습니다.

   ![홈페이지](images/%ED%99%88%ED%8E%98%EC%9D%B4%EC%A7%80.PNG)

2. 데이터 베이스 설계

   ```python
   # accounts/models.py
   
   from django.db import models
   from django.contrib.auth.models import AbstractUser
   from django.conf import settings
   
   class User(AbstractUser):
       followings = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)
   ```

   ```python
   # movies/models.py
   
   from django.db import models
   from django.conf import settings
   
   class Genre(models.Model):
       name = models.CharField(max_length=200)
   
   class Movie(models.Model):
       title = models.CharField(max_length=455)
       audience = models.IntegerField()
       poster_url = models.URLField()
       description = models.TextField()
       genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
       like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_movies")
   
   class Review(models.Model):
       content = models.CharField(max_length=499)
       score = models.IntegerField()
       movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
       user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   ```

### accounts App

1. 유저 목록

   ![유저 목록](images/%EC%9C%A0%EC%A0%80%20%EB%AA%A9%EB%A1%9D.PNG)

2. 