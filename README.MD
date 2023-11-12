# konawall-py

A rewrite of konawall-rs in Python so that image manipulation is easier and cross-platform support is sort-of easier.

## To-do

- [ ] Completely rewrite CLI
    - [ ] Provide an amount of tooling equality for CLI
        - [ ] Use the config
        - [ ] Allow specifying args, but use the argparse system, environment variables and with a config parse system simultaneously, perhaps?
            - [ ] Check if such a thing to automate that exists for Python
        - [ ] Provide a history viewer TUI / CLI application
            - [ ] Investigate best methodology to provide this; are we providing queries? Should we provide JSON?
- [ ] Ensure that platforms all work with single and multiple-monitor setting:
    - [x] macOS
    - [x] Windows
    - [ ] Linux
        - Current progress: need to set up VM
        - [ ] GNOME
        - [ ] KDE
        - [ ] XFCE
        - [ ] Cinnamon
        - [ ] MATE
        - [ ] LXDE / LXQT
        - [ ] Openbox
        - [ ] i3
        - [ ] sway
- [ ] Provide Nix packaging
- [ ] Provide installer packages for macOS and Windows, including on-startup functionality
    - [ ] macOS
    - [ ] Windows
- [ ] Acknowledge that I am reinventing a database; perhaps use a database?
    - [ ] SQLite with SQLAlchemy for the history
        - Implementation thoughts: Rotations Table has UUID, Image Foreign Keys with corresponding metadata for the monitors they were requested to fit to, the tags of the request and the tags returned in metadata, so on and so forth. A model should be provided per source for the database in this regard, because each API will have its own weird metadata. Figure out how to handle that.
            Image table would approximately be as one would expect, containing the data for the monitor and the actual original image API call, alongside other parameters we can obtain.
- [ ] Environments
    - [ ] Replace the current methodology with a class based approach for their initializations, their wallpaper setters, ...
    - [ ] Make the modular approach work with that
    - [ ] Separate this out into a separate library for doing wallpaper management
- [ ] Sources
    - [ ] Separate this out into a separate library for doing image fetching from sources
    - [ ] Turn the current konachan source into a generalized booru plugin
        - [ ] Refactor, allow custom HTTP headers and a specified URL within config
            - [ ] Test with e621
            - [ ] Test with gelbooru
            - [ ] Test with konachan
    - [ ] Randomized sources and wallpapers mapping
        - Implementation thoughts: To do this, there would need to be an intermediary between a source instance with a set of tags and another copy of that source instance with a set of tags as far as "presets" to be randomly selected from goes.
        - [ ] Allow for a system in a different source is used to fetch a wallpaper or wallpaper(s) for each monitor
        - [ ] Allow for a system in which a random source can be used to fetch a wallpaper or wallpaper(s) for each instantiation
        - [ ] Allow multiple tag sets to be utilized even within one source, chosen at random
- [ ] Replace logging system with a local data store for the history
    - Implementation thoughts: The data store ought to keep a note of the source and tags used to request it and any reasonable data that the API returned, e.g. tags, rating, other metadata...
    - [ ] Replace current file downloading system
        - [ ] Provide temporary directory as an option via config
        - [ ] Provide a permanent directory as an option via config
            - [ ] Provide a maximum number of wallpapers / history to keep via config
    - [ ] Provide tooling for browsing the history
        - [ ] Proper gallery grid UI, open in browser option, ...
        - [ ] CLI tooling for searching the history