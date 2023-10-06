# konawall-py

A rewrite of konawall-rs in Python so that image manipulation is easier and cross-platform support is sort-of easier.

## To-do

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
- [ ] Sources
    - [ ] Turn the current konachan source into a eneralized booru plugin
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