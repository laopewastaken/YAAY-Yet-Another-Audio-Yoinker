import re


def sanitize_filename(text):
    """
    Remove characters that Windows does not allow in filenames.
    """

    if not text:
        return "Unknown"

    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'[\x00-\x1f]', '', text)
    text = text.strip().rstrip('.')

    return text or "Unknown"


def limit_title(text, maximum=30):
    """
    Limit the title to a maximum number of characters.
    """

    if len(text) <= maximum:
        return text

    return text[:maximum].rstrip()


def get_filename(title, channel, media_id, extension):
    """
    Build the final YAAY filename.

    Format:
    Title - Channel - ID.extension
    """

    title = sanitize_filename(title)
    channel = sanitize_filename(channel)
    media_id = sanitize_filename(media_id)

    title = limit_title(title)

    return f"{title} - {channel} - {media_id}.{extension}"
