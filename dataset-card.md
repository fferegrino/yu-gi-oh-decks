---
license: cc-by-sa-3.0
pretty_name: Yu-Gi-Oh! Decks
tags:
- yu-gi-oh
- trading-card-games
- games
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files: "*.csv"
---

# Yu-Gi-Oh! Decks

All the Yu-Gi-Oh! decks published on [YGOPRODeck](https://ygoprodeck.com/), downloaded daily through its API. Visit YGOPRODeck for the best Yu-Gi-Oh! online experience.

Decks are sharded by deck number into files of 10,000 decks each (`00000073.csv` holds decks 730000 to 739999). `main_deck`, `extra_deck` and `side_deck` hold card IDs that match the `id` column of the [Yu-Gi-Oh! Cards](https://huggingface.co/datasets/fferegrino/yugioh-cards) dataset.

Also available on [Kaggle](https://www.kaggle.com/datasets/ioexception/yugioh-decks). The code that builds it lives at [fferegrino/yu-gi-oh-decks](https://github.com/fferegrino/yu-gi-oh-decks).

The literal and graphical information presented on this dataset Yu-Gi-Oh!, including card images, the attribute, level/rank and type symbols, and card text, is copyright of 4K Media Inc, a subsidiary of Konami Digital Entertainment, Inc.
