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
                         "role": "doc-acknowledgments"},
[...]
```

applies to this HTML fragment:

```
<section epub:type="acknowledgments" role="doc-acknowledgments">
  [...]
</section>
```

## Advanced notes
Epub types and aria roles have a 1:1 relationship. However, these proprieties might apply to multiple HTML tags, hence the need to provide the 'tag' key with a list of 'value(s)'. 