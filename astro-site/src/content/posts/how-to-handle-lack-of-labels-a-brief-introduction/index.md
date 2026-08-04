---
title: "How to Handle Lack of Labels: A Brief Introduction"
date: 2022-09-28
categories: [ml]
image: "img_0.jpg"
mediumUrl: "https://medium.com/@m.nusret.ozates/how-to-handle-lack-of-labels-a-brief-introduction-97a1e96b3e1f"
---

![Image](img_0.jpg)

Photo by [Markus Spiske](https://unsplash.com/@markusspiske?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)

Hand labeling is probably the best way to get high-quality labels, but it has some challenges.

1. It is expensive, especially if you need an expert to do the labeling. For example, you need doctors for healthcare projects.
2. It could be impossible or very hard due to privacy problems. Because hand labeling means someone has to read someone else’s data.
3. As it requires humans, it is very slow. Data labeling is boring or sometimes requires great attention so it is generally slow.
4. Slow labeling = slow iteration. Say you decided that you need 3 labels instead of 2, then you need to wait for the labeling process all again.
5. And still, labelers are human and could make mistakes. The labels could be wrong and harm the model.

Due to these challenges, some techniques have been developed to get enough high-quality data in a faster way. You still should/have to have some labeled data to get better results but with small data, you can collect much more data and much faster.

## Weak Supervision

In weak supervision, you are using your domain knowledge about the task. You give some heuristics (rules) to label data. It could be:

1. If the example contains keyword x
2. Match with regex y
3. If a word in a special list ( ex. dangerous disease list or spam words list)
4. Maybe you use semi-supervision before and you can use the output of a trained model (with limited data)

Problem: these rules are noisy so the labels will be noisy too. We don’t know which rules are more important than others and we can’t know without having some ground truth data.

Solution: When you have enough ground truth data, you can use them to decide which rules are more accurate than others and you can give them weight when labeling the data.

> Bonus point: You can transfer some of the rules for using in a similar task

Question: If these rules work so well to label data, why do we need ML models?

Answer: Because in general, their rules aren’t cover all the possible data samples, when you train an ML model with these labels it can see the pattern we couldn’t see and generate predictions for data that aren’t covered by any rule.

## Semi-supervision

**Semi-supervised learning** is an approach to machine learning that combines a small amount of labeled data with a large amount of unlabeled data during training. Semi-supervised learning falls between unsupervised learning (with no labeled training data) and supervised learning (with only labeled training data).

## Self-training

You start by training a model with your initial labeled dataset. You assume the predictions with high probability scores are correct labels, you add these labels to your training set and train a new model with this new/extended training set until you are happy with the results

## Clustering

In this method, you assume that similar examples have the same label. You can use KNN to cluster your examples and label them using their cluster.

## Perturbation

This is also a data augmentation method. The assumption is small perturbations to samples shouldn’t change the label. For example, adding white noises to the image, maybe adding blur, etc. In my last company, we used this method in an NLP task. Say we have 1000 examples, we add/remove some chars to some words, add some noise to text. It gives us two gains:

1. Num. of examples we have increased significantly
2. The model becomes more robust to grammatical mistakes. It is very common to have grammatical mistakes in chatbot applications.

> In some cases, semi-supervision approaches have reached the performance of purely supervised learning, even when a substantial portion of the labels in a given dataset has been discarded.

## Transfer Learning

Say I know math, by using the things I’ve learned in math I can learn the topics in physic much easier(I think) because I **transfer** my knowledge to a field to learn a similar field. In transfer learning, we develop a base model with a base task that is easier to collect labels/data for. Then, we use this model to train our main/downstream task with much less data than required if we would train from scratch. The most popular examples are:

1. After you trained a model with the ImageNet dataset (14,197,122 images) you can remove the classification layer, create a new classification layer for your task, and train only this layer (by freezing the other layers, they are already trained to detect base image features).
2. You train a language model by using… uhm every single text you can find on the internet and the model will learn the words’ representations (embeddings), and the language itself, and then you can train your model for your main tasks such as sentence classification

## Active Learning

Active learning is all about labeling the right data to improve your model’s accuracy. The name came from the model itself: A model is an active learner, it sends back prediction requests to be labeled by annotators.

The logic here is: You don’t want to label your samples randomly and label the right data to improve the model's accuracy with as little data as possible. The most basic method is choosing the data that the model is most uncertain about the class. Another method is training different candidate models with different hyperparameters or different slices of data and labeling the data based on disagreement among them.

The data to label can come from the pool of historical data or directly from the prediction requests that come to your model in production. The last one is probably a better way to keep the model “active” and up-to-date every time.

## An Idea

According to what we learned, we can mix most of the methods! After we have some labeled examples, we can create new training samples by perturbation (semi-supervision). Then we can train a model from these examples and add new training examples using the weak supervision method. After some iteration, we can collect the data samples that the model is most uncertain about and label them to boost the accuracy a lot more! I’ve tried the perturbation on the “tweet_eval” dataset with “emotion” configuration and improved the accuracy from %39 to 67 using the same model! Thanks a lot for reading :)

## References

1. Designing Machine Learning Systems — An Iterative Process for Production-Ready Application — Chip Huyen
2. [https://en.wikipedia.org/wiki/Semi-supervised_learning](https://en.wikipedia.org/wiki/Semi-supervised_learning)
3. [https://www.image-net.org/index.php](https://www.image-net.org/index.php)
4. Avital Oliver, Augustus Odena, Colin Raffel, Ekin D. Cubuk, and Ian J. Goodfellow, “Realistic Evaluation of Deep Semi-Supervised Learning Algorithms,” NeurIPS 2018 Proceedings
