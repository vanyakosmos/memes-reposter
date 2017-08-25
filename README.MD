# memes-reposter

This bot do:
 - fetch data from reddit and imgur
 - filter out posts that were already published
 - reformat posts data chunk into list of convenient objects
 - filter posts by tags, scores, etc
 - format and publish posts into separate channels ([for imgur](https://t.me/telemgur), [for reddit](https://t.me/pop_reddit))
 - schedule next fetch-filter-publish 
 
 It also:
 - provide set of commands to control each channel separately (commands are separated by channel namespaces)
 - schedule database clean up (remove old posts ids)
