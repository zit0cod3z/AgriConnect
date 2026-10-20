from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from .models import FarmStory
from .services import create_story, like_story
from .forms import StoryForm


class StoryFeedView(View):
    def get(self, request):
        stories = FarmStory.objects.filter(is_approved=True)
        return render(request, 'stories/story_feed.html', {'stories': stories})


class CreateStoryView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'stories/create_story.html', {'form': StoryForm()})

    def post(self, request):
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            listing = d.get('listing')
            try:
                create_story(
                    listing=listing,
                    farmer_name=request.user.get_full_name() or request.user.username,
                    title=d['title'],
                    body=d['body'],
                    photo=d.get('photo'),
                )
                messages.success(request, 'Story submitted for review!')
                return redirect('stories:feed')
            except Exception as e:
                messages.error(request, str(e))
        return render(request, 'stories/create_story.html', {'form': form})


class LikeStoryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        story = get_object_or_404(FarmStory, pk=pk, is_approved=True)
        try:
            like_story(story, request.user)
            story.refresh_from_db()
        except Exception:
            pass
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'like_count': story.like_count})
        return redirect('stories:feed')
