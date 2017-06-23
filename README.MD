# Telemgur

## About

This project provides set of abstractions 
([/autoposter](https://github.com/vaniakosmos/telemgur/tree/master/autoposter)) 
that helps to build bot for automatic posting into telegrams channels. Also there is example of usage of these abstractions 
([/src](https://github.com/vaniakosmos/telemgur/tree/master/src)): 
bot for automatic broadcasting of posts from "most viral" section of Imgur into [channel #1](https://t.me/telemgur) and the same bot for fetching images/gifs from popular subreddits and posting these images into [channel #2](https://t.me/pop_reddit).

## Abstrations

### Manager

Used for registering and managing `ChannelSetup` instances. Also it separates commands for different channels (for example in one bot you can have command `/stats` for different channels).

### ChannelSetup

Setup `Collector`, telegram commands for channel, and access restrictions (decide which commands can only be used by admins).


### Collector

Control how your bot will retrieve data and publish it.


### Scheduler

Scheduling jobs for retrieve data, publish, and clean up database.


### AbstractDB

Set of methods for database that used by classes above.
