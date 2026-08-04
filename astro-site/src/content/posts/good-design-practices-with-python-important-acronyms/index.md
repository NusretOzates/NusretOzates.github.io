---
title: "Good Design Practices with Python — Important Acronyms"
date: 2022-04-05
categories: [ml]
image: "img_0.jpg"
mediumUrl: "https://medium.com/@m.nusret.ozates/good-design-practices-with-python-important-acronyms-c590bbab733d"
---

![Image](img_0.jpg)

Photo by [Bench Accounting](https://unsplash.com/@benchaccounting?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)

## Intro

As software engineers, we write code most of the time. We have some tight deadlines and because of these deadlines, we tend to write code fast without thinking about the design. This choice comes with consequences. It actually makes you slower because you write the code so urgently that you forgot that client’s requests will change faster than you thought and when that time comes to you. It will be very hard to change your code. You will look at the code and say “oh I need to change this part and it is done” and then you will realize that the change broke a completely different part of the code, you will change that too and realize this change broke another part of your code and so on…

We don’t want that, think before coding, and give yourself some time to design architecture. Think about how you could test that chunk of code and only after that start coding. To make your life easier, there are some design “principals” out there and I will explain them with examples using Python. This is the last part of the series.

## Don’t Repeat Yourself — DRY

When writing a program, you will (probably) find yourself writing the same code again and again. When a change is required, will you change all of those same codes again? Let’s look at some examples:

```python
def function_a():
    print('conversations')
def function_b():
    print('conversations')
def function_c():
    print('conversations')
```

To add a story, let’s say “conversations” is the name of a database table we need to connect. If the name of that database somehow changes, what will you do? You will make a change 3 times and you will not that lucky about finding those functions especially if you are not the one that writes all of those codes. Instead, we can write code like that:

```python
DB_NAME = 'conversations'
def function_a():
    print(DB_NAME)
def function_b():
    print(DB_NAME)
def function_c():
    print(DB_NAME)
```

Now I can just change the DB_NAME variable’s value and do the all necessary changes at once. Now we will go one step further and look at examples with more code. Say, we are doing a credit risk program and we need to calculate a score based on the user’s info:

```python
def do_something(user: dict) -> None:
    """
    Do something with user's credit score.
    :param user: User's information
    :return: None
    """
    age = user['age']
    income = user['income']
    education = user['education']
    loan = user['loan']
    score = age * 0.2 + income * 0.7 + education * 0.6 + loan * 0.3
    # Do something with the score
def sort_users_by_score(users: list) -> list:
    """
    Sort users by credit score.
    :param users: List of users
    :return: Sorted list of users
    """
    return sorted(users, key= lambda user: user['age'] * 0.2 + user['income'] * 0.7 + user['education'] * 0.6 + user['loan'] * 0.3)
```

Maybe one day your boss come to you and said “We will change the calculation of score”. Now, you need to change all the calculations from the code, if you can find them all! A better approach is:

```python
def calculate_user_credit_score(user: dict) -> int:
    """
    Calculate the user's credit score.
    :param user: User's information
    :return: User's credit score
    """
    age = user['age']
    income = user['income']
    education = user['education']
    loan = user['loan']
    return age * 0.2 + income * 0.7 + education * 0.6 + loan * 0.3
def do_something(user: dict) -> None:
    """
    Do something with user's credit score.
    :param user: User's information
    :return: None
    """
    score = calculate_user_credit_score(user)
    # Do sometging with the score
def sort_users_by_score(users: list) -> list:
    """
    Sort users by credit score.
    :param users: List of users
    :return: Sorted list of users
    """
    return sorted(users, key=calculate_user_credit_score)
```

## You Ain’t Gonna Need It — YAGNI

Personally, this is one of the hardest things to understand clearly. Understanding the main idea is simple but putting it onto practice is way harder. This is about not doing over-engineering.

Especially when you learned about SOLID principles, you have an urge to create lots of base classes and interfaces. Let’s say you create a class to do something and then you think “Well creating a base class and making the current class a subclass of this base class could be a nice idea for future requirements”. THIS IS WRONG

1. You are doing futurology. You don’t know the future requirements or the details
2. Maybe you ain’t gonna need it and it will be a waste of your valuable time
3. That base class is being biased by the current requirements, so it’ll likely not be the correct abstraction.

> *The best approach would be to write only what’s needed now in a way that doesn’t hinder further improvements. If, later on, more requirements come in, we can think about creating a base class, abstract some methods, and perhaps we will discover a design pattern that emerged for our solution. This is also the way object-oriented design is supposed to work: bottom-up.*

## Keep It Simple — KIS

Actually, I’m kind of sure it is KISS — Keep it simple, stupid 😀 It is all about being like me LAZY. Keep it simple, implement a minimal, simplest algorithm to solve the problem. Do not add unnecessary features or shiny things into your code. I’ve seen lots of people that create awfully complex solutions for very simple problems just to show off their knowledge. Don’t be like time.

> *Remember the Zen of Python: Simple is better than complex.*

## Easier to Ask Forgiveness than Permission — EAFP and Look Before You Leap — LBYL

I think this is the first thing I disagree with the author of the book in the references section. So, EAFP is about writing the action first and handling the possible errors later, like try-except cases. LBYL is the total reverse of this approach and it says you should check what you are about to do. Let me give you a clear example:

```python
# Look before you leap approach - from book
if os.path.exists(filename):
    with open(filename) as f:
      ...
 # Easier to ask forgiveness than permission approach - from book
try:
    with open(filename) as f:
        ...
except FileNotFoundError as e:
    logger.error(e)
# Better LBYL approach - my example
if not os.path.exist(filename):
 # Create the file
with open(filename) as f:
  ...
```

From the author:

> *Particular cases might of course apply, but most of the time, you’ll find the EAFP version to be more intention-revealing. The code written this way would be easier to read because it goes directly to the task needed instead of preventively checking conditions. Put another way, in the last example, you’ll see a part of the code that tries to open a file and then process it. If the file doesn’t exist, then we handle that case. In the first example, we’ll see a function checking whether a file exists, and then trying to do something. You might argue that this is also clear, but we don’t know for sure. Maybe the file being asked about is a different one or is a function that belongs to a different layer of the program, or a leftover, and such. The second approach is less error-prone when you look at the code at first glance.*

But I don’t agree with that. For me, the last code I wrote is cleaner and just the same intention-revealing as the EAFP version. So it is up to you to choose whether you want to use EAFP or LBYL 😀

Thanks for reading!

## References

1. Clean Code in Python — Mariano Anaya
