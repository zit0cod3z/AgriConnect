import re
from django.core.exceptions import ValidationError
from django.db.models import F
from .models import FarmStory, FarmStoryLike

# Prohibited patterns: URLs, phone sequences, social handles
_PROHIBITED_PATTERNS = [
    (r'https?://\S+', 'URLs are not allowed'),
    (r'www\.\S+', 'URLs are not allowed'),
    (r'\b\d[\d\s\-\(\)]{7,}\d\b', 'Phone numbers are not allowed'),
    (r'@\w+', 'Social media handles are not allowed'),
    (r'\bwa\.me\b', 'WhatsApp links are not allowed'),
]


def validate_farm_story_text(text: str) -> list:
    """Return a list of violation descriptions for prohibited content."""
    violations = []
    for pattern, message in _PROHIBITED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(message)
    return list(set(violations))


def create_story(listing, farmer_name: str, title: str, body: str, photo=None) -> FarmStory:
    """Create a farm story after validation."""
    violations = validate_farm_story_text(body)
    if violations:
        raise ValidationError(f"Story contains prohibited content: {', '.join(violations)}")
    story = FarmStory.objects.create(
        listing=listing,
        farmer_name=farmer_name,
        title=title,
        body=body,
        photo=photo,
    )
    return story


def like_story(story: FarmStory, customer) -> FarmStoryLike:
    """Like a story. Raises ValidationError on duplicate."""
    if FarmStoryLike.objects.filter(story=story, customer=customer).exists():
        raise ValidationError('You have already liked this story.')
    like = FarmStoryLike.objects.create(story=story, customer=customer)
    FarmStory.objects.filter(pk=story.pk).update(like_count=F('like_count') + 1)
    return like
