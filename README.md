# SteamCLI

This is a simple Python scripts that (through inspection of [the API list][api-list]) should dynamically
allow you to call **any** [WebAPI from Steam][webapi-docs] (available on api.steampowered.com.)

It supports both private (i.e. "partner") APIs and public APIs. Like the api.steampowered.com, it will
**not list** any of the partner APIs unless you provide a valid publisher key. If you have a SteamWorks
account, you can find out how to create one in the [SteamWorks documentation][publisherkey-docs].

## Dependencies

The only external dependency is the excellent [requests][requests] package for Python.
You should be able to install however you install python libraries -- probably just `pip install requests`.

## Example usage

    λ steamcli.py commands ISteamNews
    > ISteamNews:
        GetNewsForApp v1 [GET]
            * uint32 appid: AppID to retrieve news for
              uint32 maxlength: Maximum length for the content to return, if this is 0 the full content is returned, if it's less then a blurb is generated to fit.
              uint32 enddate: Retrieve posts earlier than this date (unix epoch timestamp)
              uint32 count: # of posts to retrieve (default 20)
        GetNewsForApp v2 [GET]
            * uint32 appid: AppID to retrieve news for
              uint32 maxlength: Maximum length for the content to return, if this is 0 the full content is returned, if it's less then a blurb is generated to fit.
              uint32 enddate: Retrieve posts earlier than this date (unix epoch timestamp)
              uint32 count: # of posts to retrieve (default 20)
              string feeds: Comma-seperated list of feed names to return news for
    * = required argument

    λ steamcli.py call ISteamNews GetNewsForApp --appid=233250 --count=1 --maxlength=1
    {u'appnews': {u'appid': 233250,
                  u'newsitems': [{u'author': u'jables',
                                  u'contents': u'R...',
                                  u'date': 1423780439,
                                  u'feedlabel': u'Community Announcements',
                                  u'feedname': u'steam_community_announcements',
                                  u'gid': u'517122602977339882',
                                  u'is_external_url': True,
                                  u'title': u'Mid-Month Bugfix and Polish Pass',
                                  u'url': u'http://store.steampowered.com/news/externalpost/steam_community_announcements/517122602977339882'}]}}

    λ steamcli.py call ISteamApps UpToDateCheck --help
    usage: steamcli.py call ISteamApps UpToDateCheck [-h] --appid APPID --version
                                                     VERSION

    optional arguments:
      -h, --help         show this help message and exit
      --appid APPID      AppID of game
      --version VERSION  The installed version of the game

## Help output

    λ steamcli.py --help
    usage: steamcli.py [-h] [--key KEY] [--verbose] [--raw] {commands,call} ...

    positional arguments:
      {commands,call}

    optional arguments:
      -h, --help         show this help message and exit
      --key KEY, -k KEY  publisher API key for SteamWorks access (https://partner.
                         steamgames.com/documentation/webapi#creating for details)
      --verbose, -v      print verbosely
      --raw, -r          print output raw (probably JSON)


    λ steamcli.py commands --help
    usage: steamcli.py commands [-h] [interface] [method]

    list all SteamAPI commands (results will differ with & without --key)

    positional arguments:
      interface
      method

    optional arguments:
      -h, --help  show this help message and exit


    λ steamcli.py call --help
    usage: steamcli.py call [-h] [--method-version METHOD_VERSION]
                            interface method ...

    call a specific SteamAPI command

    positional arguments:
      interface
      method
      parameters

    optional arguments:
      -h, --help            show this help message and exit
      --method-version METHOD_VERSION
                            what version of the method to call, if there are
                            multiple. default is latest.


[requests]: http://docs.python-requests.org/en/latest/
[api-list]: https://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/
[webapi-docs]: https://partner.steamgames.com/documentation/webapi
[publisherkey-docs]: https://partner.steamgames.com/documentation/webapi#creating
