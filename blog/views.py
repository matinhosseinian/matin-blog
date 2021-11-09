from django.http.response import HttpResponseRedirect
from blog.forms import CommentForm
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views import View
# from datetime import date

from .models import Post
from .forms import CommentForm


class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data


class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "all_posts"


class SinglePostView(View):
    def is_stored_post(self, request, post_id):
        stored_posts = request.session.get("stored_posts")
        if stored_posts is not None:
            is_saved_for_later = post_id in stored_posts
        else:
            is_saved_for_later = False

        return is_saved_for_later

    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": CommentForm(),
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_post(request, post.id)
        }
        return render(request, "blog/post-detail.html", context)

    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()

            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))

        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by("-id"),
            "saved_for_later": self.is_stored_post(request, post.id)
        }
        return render(request, "blog/post-detail.html", context)


class ReadLaterview(View):
    def get(self, request):
        storeed_posts = request.session.get("stored_posts")

        context = {}

        if storeed_posts is None or len(storeed_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=storeed_posts)
            context["posts"] = posts
            context["has_posts"] = True

        return render(request, "blog/stored_posts.html", context)


    def post(self, request):
        storeed_posts = request.session.get("stored_posts")

        if storeed_posts is None:
            storeed_posts = []

        post_id = int(request.POST["post_id"])

        if post_id not in storeed_posts:
            storeed_posts.append(post_id)
        else:
            storeed_posts.remove(post_id)

        request.session["stored_posts"] = storeed_posts

        return HttpResponseRedirect("/")

# all_posts = [

# ]

# def get_date(post):
#     return post['date']
# def starting_page(request):
#     # sorted_posts = sorted(all_posts, key=get_date)
#     # latest_posts = sorted_posts[-3:]
#     latest_posts = Post.objects.all().order_by("-date")[:3]
#     return render(request, "blog/index.html", {
#         "posts": latest_posts
#     })


# def posts(request):
#     all_posts = Post.objects.all().order_by("-date")
#     return render(request, "blog/all-posts.html", {
#         "all_posts": all_posts
#     })


# def post_detail(request, slug):
#     identified_post = get_object_or_404(Post, slug=slug)
#     return render(request, "blog/post-detail.html", {
#         "post": identified_post,
#         "post_tags": identified_post.tags.all()
#     })
