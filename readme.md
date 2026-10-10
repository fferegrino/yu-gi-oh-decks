# Visit [YGOPRODeck](https://ygoprodeck.com/) for the best Yu-Gi-Oh! online experience.

# Yu-Gi-Oh!

A dataset downloaded daily from [https://ygoprodeck.com/](https://ygoprodeck.com/) and published on [Hugging Face](https://huggingface.co/datasets/fferegrino/yugioh-decks) and [Kaggle](https://www.kaggle.com/datasets/ioexception/yugioh-decks).

The data does not live in this repository. Each run of [dataset-sync](https://github.com/fferegrino/dataset-sync) downloads the current dataset from Hugging Face into `data/`, appends new decks with `download.py`, and uploads the result to Kaggle and then Hugging Face. To read from Kaggle instead, run the workflow manually with `source: kaggle`.

`dataset-metadata.json` describes the Kaggle dataset and `dataset-card.md` becomes the Hugging Face dataset card.
