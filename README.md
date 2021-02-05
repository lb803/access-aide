# Access Aide
_Access Aide_ is a Calibre (book editor) plugin to enhance epubs with accessibility features.

# Features
 -  Add language declaration to `<html>` tags;
 -  Map epub:type attributes to their appropriate aria role attribute.
 -  Add accessibility declarations to book metadata.

# Usage
This plugin can be used as part of an InDesign-based workflow to produce accessible epubs. InDesign is capable of adding language information to OPF files and appropriate epub:type to html tags. Access Aide reads this information and add language declarations, aria roles and metadata statements to comply with the WCAG 2.0 – AA guidelines for accessible publications.

## Config
Plugin behaviour can be fine tuned via plugin config dialogue.

![Access Aide config dialogue](docs/config_dialogue.png)

## Use
Open the book to enhance in the Calibre ebook editor and start Access Aide. This can be performed clicking Plugins -> Access Aide, or via Ctrl+Shift+a.

![Access Aide confirm dialogue](docs/confirm_dialogue.png)

# License
Source code by Luca Baffa, released under the GPL 3 licence.

This project aims to port the functionalities of the excellent [Access-Aide](https://github.com/kevinhendricks/Access-Aide) LGPL v2.1 Sigil plugin to Calibre.

The plugin icon (`./icon/icon.png`) comes from the `adwaita-icon-theme` pack ([gitlab page](https://gitlab.gnome.org/GNOME/adwaita-icon-theme) of the project), released as LGPL v3 by the GNOME Project.
