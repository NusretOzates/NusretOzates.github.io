---
title: "Transformer Models Hyperparameter Optimization With the Optuna"
date: 2021-09-21
categories: [ml]
image: "img_0.jpg"
mediumUrl: "https://medium.com/carbon-consulting/transformer-models-hyperparameter-optimization-with-the-optuna-299e185044a8"
---

![Image 1](img_0.jpg)

Photo by [Alexander Schimmeck](https://unsplash.com/@alschim?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com/?utm_source=medium&utm_medium=referral)

Before the beginning: Transformers library already has a function called `hyperparameter_search` in the `Trainer` object. But the aim of this article is to learn Optuna by using Transformers.

Some codes look bad but to make copy-paste easier, I add the code with the screenshot of the good-looking code!

## What is Hyperparameter Optimization?

A hyperparameter is a parameter whose value is used to control the learning process. By contrast, the values of other parameters (typically node weights) are learned. By changing these parameters, we can improve or worsen the accuracy of the model.

As a consequence, choosing the right hyperparameters are important. Hyperparameter optimization is the process of choosing right values for the hyperparameters through searching.

## What is Optuna?

> _Optuna is an automatic hyperparameter optimization software framework, particularly designed for machine learning. It features an imperative, define-by-run style user API. Thanks to our define-by-run API, the code written with Optuna enjoys high modularity, and the user of Optuna can dynamically construct the search spaces for the hyperparameters._
>
> _— From the official website_

With Optuna, it is easier to search for the best hyperparameters. Let's start with a simple example:

```python
import optuna
def objective(trial):
    x = trial.suggest_uniform("x", -10, 10)
    return (x - 2) ** 2
study = optuna.create_study()
study.optimize(objective, n_trials=100)
study.best_params  # E.g. {'x': 2.002108042}
```

Here we have:

1. An objective function to optimize
2. A trial object to suggest some hyperparameter values
3. A study object to run the "optimize" method and find the best value from the 100 trials.

Let's dive in and learn with a simple text classification example:

## Get the dataset

I will use the "Adverse Drug Reaction Data v2" dataset from the Huggingface Datasets.

```python
from datasets import load_dataset
dataset = load_dataset("ade_corpus_v2", "Ade_corpus_v2_classification")
```

This is how the dataset looks like:

```python
DatasetDict({
    train: Dataset({
        features: ["text", "label"],
        num_rows: 23516
    })
})
```

It doesn't contain any test data. Let's split it as train and test data.

```python
dataset = dataset["train"].train_test_split(0.2)
```

Now our dataset looks like this:

```python
DatasetDict({
    train: Dataset({
        features: ["text", "label"],
        num_rows: 18812
    })
    test: Dataset({
        features: ["text", "label"],
        num_rows: 4704
    })
})
```

Normally, to train the model you would first load the model and the tokenizer:

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
tokenizer = AutoTokenizer.from_pretrained("google/electra-small-discriminator")
model = AutoModelForSequenceClassification.from_pretrained(
    "google/electra-small-discriminator"
)
```

Then you would tokenize the dataset using the tokenizer:

```python
def preprocess(examples):
    # Tokenize, pad, or truncate to max length 128
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )
dataset = dataset.map(preprocess, batched=True)
```

Then decide training arguments (I don't have a very powerful GPU…):

```python
training_args = TrainingArguments(
    output_dir="ade-test",
    learning_rate=0.001,
    weight_decay=0.1,
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    disable_tqdm=True,
)
```

Now you are ready to train your model:

```python
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)
result = trainer.train()
training_loss = result.training_loss
```

For this example, what we want to do is find the best hyperparameters to get the minimum training loss. We will create a function named `objective`. This function will initialize the model, use different training argument values for N times and return the training loss using Optuna.

```python
def objective(trial: optuna.Trial):
    model = AutoModelForSequenceClassification.from_pretrained(
        "google/electra-small-discriminator"
    )
    training_args = TrainingArguments(
        output_dir="ade-test",
        learning_rate=trial.suggest_loguniform("learning_rate", low=4e-5, high=0.01),
        weight_decay=trial.suggest_loguniform("weight_decay", 4e-5, 0.01),
        num_train_epochs=trial.suggest_int("num_train_epochs", low=2, high=5),
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        disable_tqdm=True,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
    )
    result = trainer.train()
    return result.training_loss
```

To optimize this `objective`, we need to create a study and call its `optimize` function:

```python
# We want to minimize the loss!
study = optuna.create_study(
    study_name="hyper-parameter-search",
    direction="minimize",
)
# Optimize the objective using 15 different trials
study.optimize(func=objective, n_trials=15)
print(study.best_value)   # best loss value
print(study.best_params)  # best hyperparameter values
print(study.best_trial)   # info about the best trial
```

This is the complete code example:

```python
import optuna
from datasets import load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
dataset = load_dataset("ade_corpus_v2", "Ade_corpus_v2_classification")
dataset = dataset["train"].train_test_split(0.2)
model_name = "google/electra-small-discriminator"
tokenizer = AutoTokenizer.from_pretrained(model_name)
def preprocess(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )
dataset = dataset.map(preprocess, batched=True)
def objective(trial: optuna.Trial):
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    training_args = TrainingArguments(
        output_dir="ade-test",
        learning_rate=trial.suggest_loguniform("learning_rate", low=4e-5, high=0.01),
        weight_decay=trial.suggest_loguniform("weight_decay", 4e-5, 0.01),
        num_train_epochs=trial.suggest_int("num_train_epochs", low=2, high=5),
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        disable_tqdm=True,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
    )
    result = trainer.train()
    return result.training_loss
study = optuna.create_study(
    study_name="hyper-parameter-search",
    direction="minimize",
)
study.optimize(func=objective, n_trials=15)
print(study.best_value)
print(study.best_params)
print(study.best_trial)
```

This is just a simple example; there are lots of things to learn, such as callbacks, samplers, and pruners! Thanks for reading!

>**Note from a reader:** By default, during the first 10 trials, the random sampler is used via `TPESampler`, so we might see more improvement when we increase `n_trials` > 10.

## References

1. [https://en.wikipedia.org/wiki/Hyperparameter_optimization](https://en.wikipedia.org/wiki/Hyperparameter_optimization)
2. [https://optuna.readthedocs.io/en/stable/index.html](https://optuna.readthedocs.io/en/stable/index.html)
