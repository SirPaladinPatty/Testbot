import praw

reddit = praw.Reddit(client_id='r9iCbMevLSuhCAbBlqoakA',
                     client_secret='pmvkADXxBayrJY5kf5JlH4xJeWjErw',
                     user_agent='my user agent')

sub = 'dankmemes'

while True:
    submissions = reddit.subreddit(sub).random()
    if submissions is not None and not submissions.url.startswith("https://gfycat.com"):
        print(submissions.title)
        print(f"test(https://reddit.com{submissions.permalink} \"Hovertext\")")
        print(submissions.url)
        break

