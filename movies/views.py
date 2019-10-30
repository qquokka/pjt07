from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import ReviewForm
from django.contrib import messages

def index(request):
    context = {
        'movies': Movie.objects.all()
    }
    return render(request, 'movies/index.html', context)

def detail(request, movie_pk):
    context = {
        'movie': get_object_or_404(Movie, pk=movie_pk),
        'form': ReviewForm()
    }
    return render(request, 'movies/detail.html', context)
    
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

def review_delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        review.delete()
    else:
        messages.warning(request, '리뷰 삭제 권한이 없습니다.')
    return redirect('movies:detail', movie_pk)

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