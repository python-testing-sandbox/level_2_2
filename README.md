[![Build Status](https://travis-ci.org/katyaaa86/level_2_2.svg?branch=main)](https://travis-ci.org/katyaaa86/level_2_2)
[![codecov](https://codecov.io/gh/katyaaa86/level_2_1/branch/master/graph/badge.svg)](https://codecov.io/gh/katyaaa86/level_2_2)

# Testing sandbox level 2.2

Welcome to the testing sandbox: practice-driven testing instrument.
It can help you to get more comfortable and skilful at writing different
types of tests.

## The plan

The sandbox has five different levels. Here is an approximate plan:

1. Basics unit testing.
2. Production-ready unit testing for simple functions (you are here, this is the second part of the level).
3. Confident unit testing: advanced features, complicated mocking, tests organisation.
4. End-to-end tests mastery.
5. TDD and PBT.

Some levels can have sub-levels, and every level can have its process of completion.

Level 2 is about writing tests on more complex units of code: functions with IO.
Make sure, that your tests doesn't user disk or network: it makes them slow and unreliable.

## How to complete this level

1. Read/watch everything in a reading list.
2. You have some code in `code` module. Write tests for this code with 100% branch coverage.
3. Push tests to your fork of the repo. Make a pull-request to this repo. This is where review will happen. 
   No pull requests will be merged to this repo.
3. Ask your colleague to make a review of your code. Fix all errors.
4. Ask me (@melevir) to review your code. Fix all errors.
5. Hooray!

## Testing requirements

- Use python 3.9.
- Use latest pytest.
- Don't compose tests in `TestCase`-style classes, use modules instead.
- Setup CI/CD with automatic coverage calculation and badge with coverage in readme.

## Review how to

- Before review, make sure, that tests *branch* coverage is 100%.
- Review considered to be done when reviewer left 3+ comments.
- Use [conventional comments](https://conventionalcomments.org/).
- If you think, that some somment is not required to fix, use `non-blocking` decorator.
- Every comment without `non-blocking` decorator has to be fixed by the author of code.

## Materials

Read this before writing the first line of code:

- [Elements of Excellent Testing](https://www.developsense.com/resources/TestingSkillsv4.pdf)
- [A Rapid Software Testing Framework](https://www.satisfice.com/download/a-rapid-software-testing-framework)

Read/watch this during or after writing tests:

- [The fundamentals of unit testing (series)](https://defragdev.com/blog/2012/10/24/the-fundamentals-of-automated-testing-series.html)
- [Testing Is A Team Problem](https://janetgregory.ca/testing-is-a-team-problem/)
- [My Python testing style guide](https://blog.thea.codes/my-python-testing-style-guide/)
