from django.conf import settings
from django.core import mail
from django.core.cache import cache
from django.template.loader import render_to_string

from funfactory.urlresolvers import reverse
from tower import ugettext_lazy as _lazy

from flicks.base.util import absolutify, get_object_or_none
from flicks.videos.models import Video


VIEWS_KEY = 'VIEWCOUNT_%s'


def add_view(video_id):
    """Add a view to the view count for the video.

    Views are stored in the cache and are periodically stored back to the
    database. How often this happens depends on the view count.
    """
    # Ensure that the view count is in the cache.
    viewcount = cached_viewcount(video_id)
    if viewcount is None:
        return None

    key = VIEWS_KEY % video_id
    viewcount = cache.incr(key)
    save_viewcount = (
        (viewcount < 10) or
        (viewcount < 100 and viewcount % 5 == 0) or
        (viewcount < 1000 and viewcount % 25 == 0) or
        (viewcount > 1000 and viewcount % 100 == 0)
    )

    if save_viewcount:
        Video.objects.filter(id=video_id).update(views=viewcount)

    return viewcount


def cached_viewcount(video_id):
    """Get the viewcount for the specified video from the cache. If the
    viewcount isn't in the cache, load it from the DB and store it in the
    cache.
    """
    key = VIEWS_KEY % video_id
    viewcount = cache.get(key)
    if viewcount is None:
        video = get_object_or_none(Video, id=video_id)
        if video is None:
            return None

        cache.set(key, video.views, 0)  # Cache indefinitely
        viewcount = video.views

    return viewcount


def send_video_complete_email(video):
    """Send an email to the uploader of a video that the video conversion has
    completed.
    """
    subject = _lazy('Your Firefox Flick is ready!')
    video_url = reverse('flicks.videos.details', kwargs={'video_id': video.id})
    message = render_to_string('videos/notification_email.html', {
        'video_link': absolutify(video_url),
        'flicks_email': settings.DEFAULT_FROM_EMAIL,
        'facebook_link': settings.FACEBOOK_LINK,
        'twitter_link': settings.TWITTER_LINK
    })
    mail.send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                   [video.user.email])
