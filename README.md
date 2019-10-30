---
typora-root-url: ./
---

# Project 07: Easy Mean

##	Pair Programming을 통해 느낀점

1. 지민이는 따옴표를 쓸 때 작은 따옴표를 쓴다.
2. 혼자 할 때보다 왠지 모르게 더 피로해진다.
3. Navigator일 때는 머리가 잘 돌아가는데 키보드만 잡으면 머리가 안 돌아간다.

## 프로젝트

#### 1. `movies/index/`로 redirect하기

http://127.0.0.1:8000/로 들어갈 때 http://127.0.0.1:8000/movies/로 redirect되도록 easy_mean/urls.py 안에 함수 go_homepage를 만들었습니다.

```python
# easymean/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def go_homepage(request):
    return redirect('movies:index')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('movies/', include('movies.urls')),
    path('', go_homepage),
]
```

#### 2. DB 만들기

`accounts`앱의 `User `모델, `movies `앱의 `Movie` 모델, `Genre` 모델, `Review` 모델을 다음과 같이 정의했습니다.

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

`movies_like_movies_user` 테이블은 따로 중개모델을 만들지 않고 `Movie` 모델에서 `User` 모델과의 N:M 관계를 통해 생성하였습니다.

#### 3. `base.html`

`base.html`을 easymean/templates 안에 넣어준 후 Django가 템플릿으로 인식할 수 있도록 `settings.py`에 있는 `TEMPLATES`의 `DIRS`에 다음과 같이 추가하였습니다.

```python
# settings.py
TEMPLATES = [
    {
        'DIRS': [os.path.join(BASE_DIR, 'easymean', 'templates')],
    },
]
```

모든 페이지의 상단에서 로그인 상태를 볼 수 있도록 했고, 오류 메시지가 있다면 로그인 상태 바로 아래에 띄우도록 했습니다. 아래 사진은 다른 사람의 평점 정보를 수정하려 했을 때 오류 메시지가 뜨는 화면입니다.

![error_message](/images/error_message.PNG)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>EasyMean</title>
</head>
<body>
    <div>
        {% if user.is_authenticated %}
            <a href="{% url 'accounts:detail' user.pk %}">{{ user.username }}</a>님 환영합니다!
            <a href="{% url 'accounts:logout' %}">
                <button>로그아웃</button>
            </a>
        {% else %}
            <a href="{% url 'accounts:login' %}">
                <button>로그인</button>
            </a>
            <a href="{% url 'accounts:signup' %}">
                <button>회원가입</button>
            </a>
        {% endif %}
    </div>
    {% for message in messages %}
        <div><p>{{ message }}</p></div>
    {% endfor %}
    <hr>
    {% block body %}
        
    {% endblock %}
</body>
</html>
```



### accounts App

#### 1. 회원가입

![signup](/images/signup.PNG)

먼저, 직접 만든 `User` 모델의 경로를 `settings.py`에 등록한다.

```python
# settings.py
AUTH_USER_MODEL = 'accounts.User'
```

직접 만든 `User` 모델을 이용해 회원 가입 form을 만들기 위하여 장고에 내장되어 있는 `UserCreationForm`을 상속받는다.

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
```

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
]
```

```python
# accounts/views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            auth_login(request, form.save())  # 회원가입시 자동 로그인
            return redirect('accounts:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/form.html', context)
```

```html
<!-- accounts/form.html -->
{% extends 'base.html' %}
{% block body %}
<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">submit</button>
</form>

{% endblock  %}
```

#### 2. 로그인

![login](/images/login.PNG)

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name="login"),
]
```

```python
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm

def login(request):
    if request.user.is_authenticated:
        return redirect('accounts:index')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'movies:index')
        				# login_required를 만나서 로그인시 이전 화면으로 넘어갈 수 있도록.
    else:
        form = AuthenticationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/form.html', context)
```

```html
<!-- accounts/form.html -->
{% extends 'base.html' %}
{% block body %}
<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">submit</button>
</form>

{% endblock  %}
```

#### 3. 로그아웃

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout, name="logout"),
]
```

```python
# accounts/views.py
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return redirect('movies:index')
```

#### 4. 유저 목록

![user_list](/images/user_list.PNG)

`username`을 클릭하면 유저 상세보기 페이지로 넘어갑니다. email을 작성하지 않은 사용자는 email이 표시되지 않았습니다. 

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name="index"),
]
```

```python
# accounts/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model

def index(request):
    context = {
        'users': get_user_model().objects.all()
    }
    return render(request, 'accounts/index.html', context)
```

```html
<!-- accounts/index.html -->
{% extends 'base.html' %}

{% block body %}
<table>
    <thead>
        <tr>
            <th>id</th>
            <th>username</th>
            <th>email</th>
        </tr>
    </thead>
    <tbody>
        {% for user in users %}
            <tr>
                <td>{{ user.pk }}</td>
                <td>
                    <a href="{% url 'accounts:detail' user.pk %}">
                        {{ user.username }}
                    </a>
                </td>
                <td>{{ user.email }}</td>
            </tr>
        {% empty %}
            <tr>
                <td>아무도 없어요ㅠ</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

#### 5. 유저 상세보기

![user_detail](/images/user_detail.PNG)

해당 유저가 작성한 평점 정보와 좋아하는 영화 정보가 모두 출력되며, 각각 평점을 수정할 수 있도록 구성했습니다. 

```python
# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('<int:user_pk>/', views.detail, name="detail"),
]
```

```python
# accounts/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model

def detail(request, user_pk):
    context = {
        'user_profile': get_user_model().objects.get(pk=user_pk)
    }
    return render(request, 'accounts/detail.html', context)
```

```html
<!-- accounts/detail.html -->
{% extends 'base.html' %}

{% block body %}
    <h1>{{ user_profile.username }}님의 프로필</h1>
    <hr>
    {% if user.is_authenticated %}
        <a href="{% url 'accounts:follow' user_profile.pk %}">
            <button>
                {% if user in user_profile.followers.all %}Un{% endif %}Follow
            </button>
        </a>
    {% endif %}
    <br>
    {{ user_profile.followers.count }}명이 좋아합니다.
    
    <h3>{{ user_profile.username }}님이 작성한 평점 정보</h3>
    <ul>
        {% for review in user_profile.review_set.all %}
            <li><a href="{% url 'movies:detail' review.movie.pk %}">{{ review.movie.title }}</a>: {{ review.score }}점
            <a href="{% url 'movies:update_score' review.pk %}">
                <button>수정하기</button>
            </a>
            </li>
        {% empty %}
            <li>작성한 평점이 없어요ㅠ</li>
        {% endfor %}
    </ul>
    <br>
    <h3>{{ user_profile.username }}님이 좋아하는 영화 정보</h3>
    <ul>
        {% for movie in user_profile.like_movies.all %}
            <li><a href="{% url 'movies:detail' movie.pk %}">{{ movie.title }}</a> ({{ movie.genre.name }})</li>
        {% empty %}
            <li>좋아하는 영화가 없어요ㅠ</li>
        {% endfor %}
    </ul>
{% endblock %}
```

유저 상세보기 페이지의 수정하기 버튼을 누르면 다음과 같이 평점을 수정할 수 있는 페이지로 이동합니다. 작성자 본인이 아닐 땐 권한이 없다는 메세지를 띄워주면서 유저 상세보기 페이지로 돌아가게 하고, 평점을 성공적으로 수정했을 땐 그냥 다시 유저 상세보기 페이지로 돌아가게 합니다.

![error_message](/images/error_message.PNG)

```python
# movies/forms.py
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('content', 'score')
```

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('<int:review_pk>/update_score/', views.update_score, name="update_score"),
]
```

```python
# movies/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from django.contrib import messages

def update_score(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('accounts:detail', review.user.pk)
        else:
            form = ReviewForm(instance=review)
        context = {
            'form': form
        }
        return render(request, 'accounts/form.html', context)
    else:
        messages.warning(request, '수정 권한이 없습니다.')
    return redirect('accounts:detail', review.user.pk)
```

```python
<!-- accounts/form.html -->
{% extends 'base.html' %}
{% block body %}
<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">submit</button>
</form>

{% endblock  %}
```



### movies App

#### 1. 관리자 계정 및 관리자 페이지 생성

관리자 계정은 id : admin, pw : 123 입니다.

![admin_page](/images/admin_page.PNG)

```python
# movies/admin.py

from django.contrib import admin
from .models import Movie, Genre
# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', )

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', )

admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre, GenreAdmin)
```

#### 2. 영화 목록

영화의 이미지를 클릭하면 영화 상세보기 페이지로 넘어갑니다.

![movie_list](/images/movie_list.PNG)

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name="index"),
]
```

```python
# movies/views.py
from django.shortcuts import render
from .models import Movie

def index(request):
    context = {
        'movies': Movie.objects.all()
    }
    return render(request, 'movies/index.html', context)
```

```html
<!-- movies/index.html -->
{% extends 'base.html' %}

{% block body %}
    {% for movie in movies %}
        <a href="{% url 'movies:detail' movie.pk %}">
            <img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width:20vw;">
        </a>
    {% empty %}
        <p>영화가 없어요</p>
    {% endfor %}
{% endblock %}
```

#### 3. 영화 상세보기

영화 관련 정보를 모두 나열했고, 모든 사람이 평점 목록을 볼 수 있게 했습니다. 영화가 존재하지 않는 경우 404 페이지가 나오고, 로그인 한 사람만 영화 평점을 남길 수 있습니다.

영화 평점 작성자의 아이디를 누르면 해당 유저 상세보기 페이지로 넘어갑니다.

![movie_detail](/images/movie_detail.PNG)

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('<int:movie_pk>/', views.detail, name="detail"),
]
```

```python
# movies/views.py
from django.shortcuts import render, get_object_or_404
from .forms import ReviewForm

def detail(request, movie_pk):
    context = {
        'movie': get_object_or_404(Movie, pk=movie_pk),
        'form': ReviewForm()
    }
    return render(request, 'movies/detail.html', context)
```

```html
<!-- movies/detail.html -->
{% extends 'base.html' %}

{% block body %}
<img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width:20vw;">
<h3>제목: {{ movie.title }}</h3>
<hr>
<p>관객수: {{ movie.audience }}명</p>
<p>장르: {{ movie.genre.name }}</p>
<p>줄거리: {{ movie.description }}</p>
{% if user.is_authenticated %}
    <form action="{% url 'movies:like' movie.pk %}" method="POST">
        {% csrf_token %}
        <button type="submit">좋아요{% if movie in user.like_movies.all %}취소{% endif %}({{ movie.like_users.count }})</button>
    </form>
{% endif %}
<a href="{% url 'movies:index' %}"><button>돌아가기</button></a>
{% for review in movie.review_set.all %}
    <p><a href="{% url 'accounts:detail' review.user.pk %}">{{ review.user.username }}</a>: {{ review.content }} ({{ review.score }}점)</p>
    {% if user == review.user %}
        <form action="{% url 'movies:review_delete' movie.pk review.pk %}" method="POST" onclick="return confirm('삭제하시겠습니까?')">
            {% csrf_token %}
            <button type="submit">삭제하기</button>
        </form>
    {% endif %}
{% empty %}
    <p>평점이 없어요</p>
{% endfor %}

{% if user.is_authenticated %}
    <form action="{% url 'movies:review_create' movie.pk %}" method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">확인</button>
    </form>
{% endif %}
{% endblock %}
```

#### 4. 평점 생성

로그인 한 사람만 영화평을 남길 수 있도록 했습니다. 평점 생성 URL은 `POST /movies/{movie_pk}/reviews/new/`의 형태로 만들었습니다. 입력한 평점을 검증을 통해 유효한 경우 데이터베이스에 저장하며, 저장한 경우와 아닌 경우 모두 영화 상세보기 페이지로 redirect시켰습니다. 영화가 존재하지 않는 경우에는 404 페이지를 보여주도록 했습니다.

아래의 두 사진을 비교하면 로그인 했을 때와 로그인하지 않았을 때, 평점 입력란의 유무를 알 수 있습니다.

![movie_detail](/images/movie_detail.PNG)![review_logout](/images/review_logout.PNG)

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('<int:movie_pk>/reviews/new/', views.review_create, name="review_create"),
]
```

```python
# movies/views.py
from django.shortcuts import redirect, get_object_or_404
from .forms import ReviewForm
from django.contrib import messages

@require_POST
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie = movie
            review.save()
    else:
        messages.warning(request, '로그인이 필요합니다.')
    return redirect('movies:detail', movie_pk)
```

```html
<!-- movies/detail.html -->
{% extends 'base.html' %}

{% block body %}
<img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width:20vw;">
<h3>제목: {{ movie.title }}</h3>
<hr>
<p>관객수: {{ movie.audience }}명</p>
<p>장르: {{ movie.genre.name }}</p>
<p>줄거리: {{ movie.description }}</p>
{% if user.is_authenticated %}
    <form action="{% url 'movies:like' movie.pk %}" method="POST">
        {% csrf_token %}
        <button type="submit">좋아요{% if movie in user.like_movies.all %}취소{% endif %}({{ movie.like_users.count }})</button>
    </form>
{% endif %}
<a href="{% url 'movies:index' %}"><button>돌아가기</button></a>
{% for review in movie.review_set.all %}
    <p><a href="{% url 'accounts:detail' review.user.pk %}">{{ review.user.username }}</a>: {{ review.content }} ({{ review.score }}점)</p>
    {% if user == review.user %}
        <form action="{% url 'movies:review_delete' movie.pk review.pk %}" method="POST" onclick="return confirm('삭제하시겠습니까?')">
            {% csrf_token %}
            <button type="submit">삭제하기</button>
        </form>
    {% endif %}
{% empty %}
    <p>평점이 없어요</p>
{% endfor %}

{% if user.is_authenticated %}
    <form action="{% url 'movies:review_create' movie.pk %}" method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">확인</button>
    </form>
{% endif %}
{% endblock %}
```

#### 5. 평점 삭제

평점 작성자 본인만 삭제할 수 있게 했습니다. 평점 삭제 URL은 `POST /movies/{movie_pk}/reivews/{review_pk}/delete/` 형식으로 만들었습니다. 평점 삭제 후 해당 영화의 상세보기 페이지로 redirect시켰습니다. 또한, 영화가 존재하지 않는 경우 404 페이지가 나타납니다.

평점 작성자 본인이 아니면 삭제할 수 없도록 삭제 버튼도 보이지 않게 했습니다.

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('<int:movie_pk>/reviews/<int:review_pk>/delete/', views.review_delete, name="review_delete"),
]
```

```python
# movies/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def review_delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        review.delete()
    else:
        messages.warning(request, '리뷰 삭제 권한이 없습니다.')
    return redirect('movies:detail', movie_pk)
```

```html
<!-- movies/detail.html -->
{% extends 'base.html' %}

{% block body %}
<img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width:20vw;">
<h3>제목: {{ movie.title }}</h3>
<hr>
<p>관객수: {{ movie.audience }}명</p>
<p>장르: {{ movie.genre.name }}</p>
<p>줄거리: {{ movie.description }}</p>
{% if user.is_authenticated %}
    <form action="{% url 'movies:like' movie.pk %}" method="POST">
        {% csrf_token %}
        <button type="submit">좋아요{% if movie in user.like_movies.all %}취소{% endif %}({{ movie.like_users.count }})</button>
    </form>
{% endif %}
<a href="{% url 'movies:index' %}"><button>돌아가기</button></a>
{% for review in movie.review_set.all %}
    <p><a href="{% url 'accounts:detail' review.user.pk %}">{{ review.user.username }}</a>: {{ review.content }} ({{ review.score }}점)</p>
    {% if user == review.user %}
        <form action="{% url 'movies:review_delete' movie.pk review.pk %}" method="POST" onclick="return confirm('삭제하시겠습니까?')">
            {% csrf_token %}
            <button type="submit">삭제하기</button>
        </form>
    {% endif %}
{% empty %}
    <p>평점이 없어요</p>
{% endfor %}

{% if user.is_authenticated %}
    <form action="{% url 'movies:review_create' movie.pk %}" method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">확인</button>
    </form>
{% endif %}
{% endblock %}
```

#### 6. 영화 좋아요 기능

로그인 한 유저만 좋아하는 영화를 담아 놓을 수 있습니다. 로그인하지 않으면 영화 상세 정보 밑에 있는 좋아요 버튼이 보이지 않게 숨겼습니다. 좋아요 버튼에 좋아요를 누른 사람이 몇 명인지 괄호()를 안에 표시하였습니다. 좋아요 버튼을 누른 상태일 땐 좋아요 버튼이 '좋아요 취소' 버튼으로 나타나게 했습니다. URL은 `POST /movies/{movie_pk}/like/` 형식으로 만들었습니다. 영화가 존재하지 않는 경우 404 페이지가 나타납니다.

![like_button](/images/like_button.PNG)

```python
# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('<int:movie_pk>/like/', views.like, name='like'),
]
```

```python
# movies/views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@require_POST
def like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user.is_authenticated:
        if movie in request.user.like_movies.all():
            request.user.like_movies.remove(movie)
        else:
            request.user.like_movies.add(movie)
    else:
        messages.warning(request, '로그인이 필요한 기능입니다.')
    return redirect('movies:detail', movie_pk)
```

```html
<!-- movies/detail.html -->
{% extends 'base.html' %}

{% block body %}
<img src="{{ movie.poster_url }}" alt="{{ movie.title }}" style="width:20vw;">
<h3>제목: {{ movie.title }}</h3>
<hr>
<p>관객수: {{ movie.audience }}명</p>
<p>장르: {{ movie.genre.name }}</p>
<p>줄거리: {{ movie.description }}</p>
{% if user.is_authenticated %}
    <form action="{% url 'movies:like' movie.pk %}" method="POST">
        {% csrf_token %}
        <button type="submit">좋아요{% if movie in user.like_movies.all %}취소{% endif %}({{ movie.like_users.count }})</button>
    </form>
{% endif %}
<a href="{% url 'movies:index' %}"><button>돌아가기</button></a>
{% for review in movie.review_set.all %}
    <p><a href="{% url 'accounts:detail' review.user.pk %}">{{ review.user.username }}</a>: {{ review.content }} ({{ review.score }}점)</p>
    {% if user == review.user %}
        <form action="{% url 'movies:review_delete' movie.pk review.pk %}" method="POST" onclick="return confirm('삭제하시겠습니까?')">
            {% csrf_token %}
            <button type="submit">삭제하기</button>
        </form>
    {% endif %}
{% empty %}
    <p>평점이 없어요</p>
{% endfor %}

{% if user.is_authenticated %}
    <form action="{% url 'movies:review_create' movie.pk %}" method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">확인</button>
    </form>
{% endif %}
{% endblock %}
```

