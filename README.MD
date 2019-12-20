# Memes Reposter

Service for stealing content from different sources and reposting them to telegram channels

### List of some channels that use this bot

- [reddit ~ rad](https://t.me/radchan)
- [imgur ~ telemgur](https://t.me/telemgur)
- rss feeds:
	- [The Verge](https://t.me/verge_media)
	- [WIRED](https://t.me/wired_media)
	- [TechCrunch](https://t.me/techcrunch_media)


### How it works

Publishing task (run every 30 minutes):
- fetch posts from somewhere
- filter out posts that were already poster
- filter out trash: low score, bad tags, etc
- format post: album or single image with title or whatever
- send to the telegram

Clean up task (run at midnight):
- delete old posts from database
