#  MIT License Copyright (c) 2020. Houfu Ang
import random

import spacy
from spacy.util import minibatch, compounding


def train_model(model="line_model", output_dir="line_model", n_iter=20, n_texts=2000, init_tok2vec=None,
                train_file='test_lines_1.csv'):
    nlp = load_model(model)

    if "textcat" not in nlp.pipe_names:
        textcat = nlp.create_pipe(
            "textcat", config={"exclusive_classes": True}
        )
        nlp.add_pipe(textcat, last=True)
    # otherwise, get it, so we can add labels to it
    else:
        textcat = nlp.get_pipe("textcat")

    textcat.add_label("NA")
    textcat.add_label("Remove")

    print("Loading test data...")
    (train_texts, train_cats), (dev_texts, dev_cats) = train_load_data(train_file=train_file)
    train_texts = train_texts[:n_texts]
    train_cats = train_cats[:n_texts]
    print(f'Using {n_texts} examples ({len(train_texts)} training, {len(dev_texts)} evaluation)')
    train_data = list(zip(train_texts, [{"cats": cats} for cats in train_cats]))

    # get names of other pipes to disable them during training
    pipe_exceptions = ["textcat", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):  # only train textcat
        optimizer = nlp.begin_training()
        if init_tok2vec is not None:
            with init_tok2vec.open("rb") as file_:
                textcat.model.tok2vec.from_bytes(file_.read())
        print("Training the model...")
        print("{:^5}\t{:^5}\t{:^5}\t{:^5}".format("LOSS", "P", "R", "F"))
        batch_sizes = compounding(4.0, 32.0, 1.001)
        for i in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            random.shuffle(train_data)
            batches = minibatch(train_data, size=batch_sizes)
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.2, losses=losses)
            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = train_evaluate(nlp.tokenizer, textcat, dev_texts, dev_cats)
            print(
                "{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}".format(  # print a simple table
                    losses["textcat"],
                    scores["textcat_p"],
                    scores["textcat_r"],
                    scores["textcat_f"],
                )
            )

    # test the trained model
    test_text = "This movie sucked"
    doc = nlp(test_text)
    print(test_text, doc.cats)

    if output_dir is not None:
        with nlp.use_params(optimizer.averages):
            nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        print(test_text, doc2.cats)


def train_load_data(train_file, limit=0, split=0.8):
    import csv
    with open(train_file) as csv_file:
        contents = csv.reader(csv_file)
        train_data = []
        for row in contents:
            train_data.append((row[0], row[1]))
    random.shuffle(train_data)
    train_data = train_data[-limit:]
    text, labels = zip(*train_data)
    cats = [{"NA": bool(y == 'NA'), "Remove": not bool(y == 'NA')} for y in labels]
    split = int(len(train_data) * split)
    return (text[:split], cats[:split]), (text[split:], cats[split:])


def train_evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if label == "NEGATIVE":
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"textcat_p": precision, "textcat_r": recall, "textcat_f": f_score}


def load_model(model='line_model'):
    return spacy.load(model)


class PDPCLineClassifier():
    def __init__(self, model='line_model'):
        self.model = load_model(model)

    def categorise(self, text):
        doc = self.model(text)
        return doc.cats["NA"] > 0.95


if __name__ == '__main__':
    train_model()
