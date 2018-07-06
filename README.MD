# Memes Reposter

Service that steal memes from different sources and repost its to telegram.

### List of some channels

- [reddit ~ rad](https://t.me/pop_reddit)
- [imgur ~ telemgur](https://t.me/telemgur)


### How it works

Publishing task (run every 30 minutes):
- fetch posts from somewhere
- filter out posts that were already poster
- filter out trash: low score, bad tags, etc
- format post: album or single image with title or whatever
- publish to the telegram

Clean up task (run at midnight):
- delete old posts from database
