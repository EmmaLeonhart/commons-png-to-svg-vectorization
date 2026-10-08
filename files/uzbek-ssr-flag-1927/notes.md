# Flag of the Uzbek Soviet Socialist Republic (1927-1929)

- **Target:** [File:Flag of the Uzbek Soviet Socialist Republic(1927-1929).png](https://commons.wikimedia.org/wiki/File:Flag_of_the_Uzbek_Soviet_Socialist_Republic(1927-1929).png),
  752×381, by Whaales (2020), drawn in paint.net from the Wikipedia description. CC BY 4.0.
- **Rebuilt as:** a `#cd0000` rect plus three `<text>` lines in `#ffd700`, colours taken from the PNG.
  The lines are Uzbek in Arabic script (`أوز.ئـ.شـ.جـ.`), Russian `Уз.С.С.Р`, and Uzbek in
  Arabic script (`جـ.شـ.ا.اوز.`). The Arabic lines are `direction="rtl"` with x at their right edge,
  so the trailing full stops land on the left as in the PNG. CC BY 4.0 with attribution to Whaales.
- **Method:** `python files/uzbek-ssr-flag-1927/build.py`. The Cyrillic line matches the PNG's ink box
  exactly. The PNG's Arabic glyphs come from a different font, so those lines are matched by
  width and baseline (within 1 px); glyph heights and shapes differ.
- **Check before upload:** the Arabic transcription was read off the image. Someone who reads the
  1920s Uzbek Arabic orthography should confirm it, especially whether the first letter is أ.
- **Checked:** in Chrome against the PNG.
