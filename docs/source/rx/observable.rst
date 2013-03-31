:mod:`observable`
======================

.. module:: rx.observable
   :synopsis: Observable implementation.

.. **Source code:** :source:`rx/observable.py`

Observables are similar to iterables in that they yield values until
either an Exception gets raised or the sequence completes. But in contrast
to iterables one can not explicitly request an :class:`Observable` to yield
the next value but the next value will be yielded when it is generated.

Thus a good example for an Observable is an event. Every time the event
gets raised, the Observable produces its next value and sends it down
the pipeline.

The power of RxPython comes from the fact that it provides a set of Operators
to create, merge, split and await Observables. The operators are named like
SQL keywords on purpouse to make the library easier to use and understand.

In the following documentation the operators are split up into specific domains
like aggregation, blocking and multiple to make the overall navigation easier.

Some most of the names of the operators are directly ported from the C# original
implementation, some were renamed to integrate with the python native names
more directly. It is clear that many of the things are not implemented in the
most ideomatic way. This is just because the first milestone was to get the
whole library working. Further optimisations can be made later.


.. class:: Observable

	.. method:: subscribe(observer)
				subscribe(onNext[, onError=None[, onCompleted=None]])

		If no observer is provided but instead any of the methods ``onNext``,
		``onError``, or ``onCompleted`` an anonymous
		:class:`Observer <rx.observer.Observer>` will be created.

		Subscribes the observer for the sequence.


.. class:: AnonymouseObservable(subscribe)

	Represents an :class:`Observable` that calls the provided subscribe
	function every time an :class:`Observer <rx.observer.Observer> subscribes.

	The observer will be passed as parameter to the subscribe function.

	The subscribe funtion should return a
	:class:`Disposable <rx.disposable.Disposable>`.


.. class:: ConnectableObservable(source, subject)

	Represents an :class:`Observable` that connects the ``source`` to
	``subject`` when :meth:`connect` gets called.

	If the :class:`Disposable <rx.disposable.Disposable>` returned by
	connect gets disposed. The connection between the observable and
	the subject is destroyed again.

	.. method:: subscribe(observer)
				subscribe(onNext[, onError=None[, onCompleted=None]])

		Returns the result of subscribing to ``subject``.

.. class:: GroupObservable

	Represents an :class:`Observable` that has a key. Most likely it
	resulted from a groupby call.

	.. attribute:: key

		The key of this Observable sequence.


Aggregation
-----------

.. class:: Observable

	.. method:: aggregate(seed, accumulator[, resultSelector=identity])

		Aggregates the values of the :class:`Observable`. When the source
		completes, ``resultSelector(accumulation)`` is yielded as next value.

	.. method:: all(predicate)

		Yields True if ``predicate`` returns True for all values.

	.. method:: any([predicate=truePredicate])

		Yields True if ``predicate`` returns True for any value.

	.. method:: average([selector=identity])

		Yields the average value of ``selector(value)`` for all values.

	.. method:: contains(value[, equals=defaultEquals])

		Yields True if ``equals(value, onNextValue)`` returns True for
		any value.

	.. method:: count([predicate=truePredicate])

		Yields how often ``predicate(value)`` returned True.

	.. method:: elementAt(index)

		Yields the value at index ``index`` or Exception.

	.. method:: elementAtOrDefault(index[, default=None])

		Yields the value at index ``index`` or default.

	.. method:: firstAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value)``
		returns True or Exception.

	.. method:: firstAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value)``
		or default.

	.. method:: isEmpty()

		Yields True if the Observable contains no values.

	.. method:: lastAsync([predicate=truePredicate])

		Yields the last value or Exception.

	.. method:: lastAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the last value or default.

	.. method:: max([compareTo=defaultCompareTo])

		Yields the maximum value. The maximum value is the value
		where ``compareTo(value, currentMax)`` returns 1 at
		the end.

	.. method:: maxBy(keySelector[, compareTo=defaultCompareTo])

		Yields the maximum value. The maximum value is the value
		where ``compareTo(keySelector(value), currentMax)``
		returns 1 at the end.

	.. method:: min([compareTo=defaultCompareTo])

		Yields the minimum value. The minimum value is the value
		where ``compareTo(value, currentMin)`` returns -1 at
		the end.

	.. method:: minBy(keySelector[, compareTo=defaultCompareTo])

		Yields the minimum value. The minimum value is the value
		where ``compareTo(keySelector(value), currentMin)``
		returns -1 at the end.

	.. method:: sequenceEqual(other[, equals=defaultEquals])

		Yields True if both Observables yield the same values
		in the same order and complete.

	.. method:: singleAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value)``
		returns True or Exception. If more than one value passes
		the predicate, an Exception is yielded.

	.. method:: singleAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value)``
		returns True or default. If more than one value passes
		the predicate, an Exception is yielded.

	.. method:: sum([selector=identity])

		Yields the sum of ``selector(value)``.

	.. method:: toDictionary([keySelector=identity, elementSelector=identity])

		Yields a dict having every value inserted as
		``dict[keySelector(value)] = elementSelector(value)``.

		If multiple values have the same key, an Exception is yielded.

	.. method:: toList()

		Yields a list containing all values.


Binding
-------

.. class:: Observable

	.. method:: multicast(subject)

		Returns a :class:`ConnectableObservable` that connects the
		current sequence and ``subject``.

	.. method:: multicastIndividual(subjectSelector, selector)

		Connects the current Observable to the :class:`rx.subject.Subject`
		returned by ``subjectSelector()`` and yields the values yielded by
		the :class:`Observable` returned by
		``selector(subject from subjectSelector())``.

	.. method:: publish([initialValue=None])

		Equivalent to::

			if initialValue == None:
			    return self.multicast(Subject())
			else:
			    return self.multicast(BehaviorSubject(intialValue))

	.. method:: publishIndividual(selector[, initialValue=None])

		Equivalent to::

			if initialValue == None:
			    return self.multicastIndividual(lambda: Subject(), selector)
			else:
			    return self.multicastIndividual(lambda: BehaviorSubject(initialValue), selector)

	.. method:: publishLast([selector=None])

		Equivalent to::

			if selector == None:
			    return self.multicast(AsyncSubject())
			else:
			    return self.multicastIndividual(lambda: AsyncSubject(), selector)

	.. method:: refCount()

		Connects to the current :class:`ConnectableObservable` and shares the
		subscription with all subscribers to :meth:`refCount`


		.. note::

			Can only ne used on a :class:`ConnectableObservable`.

	.. method:: replay([selector=None, bufferSize=sys.maxsize, window=sys.maxsize, scheduler=Scheduler.currentThread])

		Replays the current :class:`Observable` whenever an
		:class:`Observer <rx.observer.Observer>` subscribes.

		If ``selector != None`` then ``selector(self)`` is replayed.

		``bufferSize`` specifies the maximum number of values that will
		be remembered.

		``window`` specifies for how long values should be remembered.

		``scheduler`` specifies the :class:`rx.scheduler.Scheduler` on which
		the remembered values will be replayed. The default is on the subscribers
		thread.


Blocking
--------

.. class:: Observable

	.. method:: collect(getInitialCollector, merge[, getNewCollector=None])

		The initial accumulator is ``getInitialCollector()``.

		On every value `accumulator = merge(accumulator, value)` is called.

		If ``getNewCollector`` is None, it is replaced with
		``lambda _: getInitialCollector``.

		Returns an iterable whos next value is the current accumulator which
		then gets replaced by ``getNowCollector(accumulator)``.

	.. method:: first([predicate=None])

		Returns the first value in the sequence or raises an Exception
		if the sequence is empty.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: firstOrDefault([predicate=None, default=None])

		Returns the first value in the sequence or ``default``.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: forEach(onNext)

		Calls ``onNext(value)`` for every value in the sequence. Blocks until
		the sequence ends.

	.. method:: forEachEnumerate(onNext)

		Calls ``onNext(value, index)`` for every value in the sequence. Blocks until
		the sequence ends.

	.. method:: getIterator()
			  __iter__()

		Returns an iterator that yields all values of the sequence.

	.. method:: last([predicate=None])

		Returns the last value in the sequence or raises an Exception
		if the sequence is empty.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: lastOrDefault([predicate=None, default=None])

		Returns the last value in the sequence or ``default``.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: latest()

		Returns an iterator that blocks for the next values but in
		contrast to :meth:`getIterator` also does not buffer values.

		This means that the iterator returns the value that arrived
		latest but it will not return a value twice.

	.. method:: mostRecent(initialValue)

		Returns an iterator that returns values even if no new values
		have arrived. It is a sampling iterator.

		This means that the iterator can yield duplicates.

	.. method:: next()

		Returns an iterator that blocks until the next value arrives.

		If values arrive before the iterator moves to the next value,
		they will be dropped. :meth:`next` only starts waiting for the
		next value after the iterator requested for it.

	.. method:: single([predicate=None])

		Returns the last value in the sequence or raises an Exception
		if the sequence is empty. If more than one value arrive, an
		Exception is raised.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: singleOrDefault([predicate=None, default=None])

		Returns the single value in the sequence or ``default``.
		If more than one value arrive, an Exception is raised.

		If ``predicate != None``, the sequence is filtered for values
		where ``predicate(value) == True``.

	.. method:: wait()

		Is a synonym for :meth:`last`














