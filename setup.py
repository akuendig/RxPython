#!/usr/bin/env python

from distutils.core import setup

long_description = """
The Reactive Extensions (Rx) is a library for composing asynchronous and
event-based programs using observable sequences and C# LINQ-style query operators.
Using Rx, developers represent asynchronous data streams with Observables,
query asynchronous data streams using LINQ operators,
and parameterize the concurrency in the asynchronous data streams using Schedulers.
Simply put, Rx = Observables + LINQ + Schedulers.
"""

version = "0.1"

setup(name="RxPython",
      version=version,
      description="An event processing library",
      long_description=long_description,
      author="Adrian Kündig",
      author_email="adriankue@gmail.com",
      url="http://akuendig.github.com/RxPython/",
      packages = [
        "rx",
        "rx.linq",
      ],
      classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.3",
        "Operating System :: OS Independent",
        # "Topic :: Software Development :: Testing",
        # "Topic :: Software Development :: Quality Assurance",
      ]
)