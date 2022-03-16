The data of `epubtype-aria-map.json` and `epubtype-aria-map.json` can be referenced at [EPUB Type to ARIA Role Authoring Guide](https://idpf.github.io/epub-guides/epub-aria-authoring/) by idpf.

# `epubtype-aria-map.json` file
This json file helps mapping epub types with corresponding aria roles.

Information included are:
 -  _Epub type_ name;
 -  _HTML tags_ where the epub type applies;
 -  The corresponding _aria role_.

So that, this fragment of this json file:

```
[...]
    "acknowledgments" : {"tag": ["section"],
                         "aria": "doc-acknowledgments"},
[...]
```

applies to this HTML fragment:

```
<section epub:type="acknowledgments" role="doc-acknowledgments">
  [...]
</section>
```

# `extra-tags.json` file
This files contains a list of additional HTML tags which accept any role value (on top of the ones already defined in `epubtype-aria-map.json`).

Exception has been made for `a` and `img` which are considered special cases as:
 -  `a` (accepted if without an href attribute)
 -  `img` (accepted only with alt text)

These exceptions are hardcoded in the add_aria() method.

# `acc_feature_values.json` file
This is a list of features which are helpful for accessibility. These can be added as metadata under _accessibilityFeature_.
