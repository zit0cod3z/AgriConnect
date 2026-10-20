from django.db import models


class FarmStory(models.Model):
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='stories', null=True, blank=True)
    farmer_name = models.CharField(max_length=200)
    title = models.CharField(max_length=300)
    body = models.TextField()
    photo = models.ImageField(upload_to='stories/%Y/%m/', null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stories_farm_story'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FarmStoryLike(models.Model):
    story = models.ForeignKey(FarmStory, on_delete=models.CASCADE, related_name='likes')
    customer = models.ForeignKey('accounts.Customer', on_delete=models.CASCADE, related_name='story_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stories_farm_story_like'
        unique_together = [('story', 'customer')]

    def __str__(self):
        return f"{self.customer} likes {self.story}"
