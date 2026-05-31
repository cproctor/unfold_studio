from collections import Counter


def get_top_genres(queryset, n):
    """Return the n most-common genre tag strings from a queryset with a genres JSONField."""
    counts = Counter()
    for genres in queryset.values_list('genres', flat=True):
        if genres:
            counts.update(genres)
    return [genre for genre, _ in counts.most_common(n)]


def genre_label(tag):
    """Human-readable label for a genre tag string."""
    return tag.replace('_', ' ').replace('-', ' ').title()
