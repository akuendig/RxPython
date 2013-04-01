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

	Represents an :class:`Observable` that calls ``subscribe``
	every time an :class:`Observer <rx.observer.Observer>` subscribes.

	The observer will be passed as parameter to ``subscribe``.

	``subscribe`` should return a
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

		The key of this :class:`Observable`.


Aggregation
-----------

.. class:: Observable

	.. method:: aggregate(seed, accumulator[, resultSelector=identity])

		Aggregates the values of the :class:`Observable`. When the source
		completes, ``resultSelector(accumulation)`` is yielded as next value.

	.. method:: all(predicate)

		Yields True if ``predicate`` returns ``True`` for all values.

	.. method:: any([predicate=truePredicate])

		Yields True if ``predicate`` returns ``True`` for any value.

	.. method:: average([selector=identity])

		Yields the average value of ``selector(value)`` for all values.

	.. method:: contains(value[, equals=defaultEquals])

		Yields True if ``equals(value, onNextValue)`` returns ``True`` for
		any value.

	.. method:: count([predicate=truePredicate])

		Yields how often ``predicate(value)`` returned True.

	.. method:: elementAt(index)

		Yields the value at index ``index`` or Exception.

	.. method:: elementAtOrDefault(index[, default=None])

		Yields the value at index ``index`` or default.

	.. method:: firstAsync([predicate=truePredicate])

		Yields the first value where ``predicate(value)``
		returns ``True`` or Exception.

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
		returns ``True`` or Exception. If more than one value passes
		the predicate, an Exception is yielded.

	.. method:: singleAsyncOrDefault([predicate=truePredicate, default=None])

		Yields the first value where ``predicate(value)``
		returns ``True`` or default. If more than one value passes
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


Concurrent
----------

.. class:: Observable

	.. method:: subscribeOn(scheduler)

		Whenever an :class:`Observer <rx.observer.Observer>` wants to
		subscribe, the actual subscription is scheduled immediatly on
		``scheduler``.

	.. method:: observeOn(scheduler)

		Whenever an onNext, onError, or onCompleted event happens, the
		invocation of the corresponding function on all observers is
		scheduled on ``scheduler``.

	.. method:: synchronize([gate=None])

		Whenever an onNext, onError, or onCompleted event happens, the
		invocation of the corresponding function on all observers is
		synchronized with ``gate``.

		If ``gate == None`` then ``gate = RLock()``.

		The synchronisation guarantees that one observer only sees one
		onNext, onError, or onComplete at the same time.


Creation
--------

.. class:: Observable

	.. staticmethod:: create(subscribe)

		Returns an :class:`Observable` that calls ``subscribe``
		every time an :class:`Observer <rx.observer.Observer>` subscribes.

		The observer will be passed as parameter to ``subscribe``.

		``subscribe`` should return a
		:class:`Disposable <rx.disposable.Disposable>`.

	.. staticmethod:: defer(observableFactory)

		Returns an :class:`Observable` that subscribes observers
		to the :class:`Observable` returned by ``observableFactory``.

		It calls ``observableFactory`` every time a subscription happens.

	.. staticmethod:: empty()

		Returns an :class:`Observable` that instantly completes
		on every subscription.

	.. staticmethod:: generate(initialState, condition, iterate, resultSelector[, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` who represents the following generator::

			currentState = initialState

			while condition(currentState):
				yield resultSelector(currentState)
				currentState = iterate(currentState)

		The values are scheduled on ``scheduler``.

	.. staticmethod:: never()

		Returns an :class:`Observable` that has no values and never completes,

	.. staticmethod:: range(start, count[, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` that yields ``count`` values beginning
		from ``start``.

		The values are scheduled on ``scheduler``.

	.. staticmethod:: repeatValue(value[, count=None, scheduler=Scheduler.iteration])

		Returns an :class:`Observable` that yields ``value`` ``count`` times and
		then completes.

		If ``count == None`` ``value`` gets yielded indefinetly.

		The values are scheduled on ``scheduler``.

	.. staticmethod:: returnValue(value[, scheduler=Scheduler.constantTimeOperations])

		Returns an :class:`Observable` that yields ``value`` and then completes.

		The value is scheduled on ``scheduler``.

	.. staticmethod:: start(action[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that yields the result of ``action()``
		scheduled for execution on ``scheduler``.

	.. staticmethod:: throw(exception[, scheduler=Scheduler.constantTimeOperations])

		Returns an :class:`Observable` that yields exception as onError.

		The exception is scheduled on ``scheduler``.

	.. staticmethod:: using(resourceFactory, observableFactory)

		Returns an :class:`Observable` that whenever an observer subscribes,
		calls ``resourceFactory()`` then ``observableFactory(resource)`` and
		subscribes the observer to the :class:`Observable` returned by
		``observableFactory``

		The resource returned by ``resourceFactory`` must have a ``dispose``
		method that is invoked once the :class:`Observable` returned by
		``observableFactory`` has completed.

	.. staticmethod:: fromFuture(future)

		Returns an :class:`Observable` that yields the value or exception
		of ``future``. If ``future`` is canceled, an Exception("Future was cancelled")
		is yielded.

	.. staticmethod:: fromIterable(iterable[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that yields all values from ``iterable``
		on ``scheduler``.

	.. staticmethod:: fromEvent(addHandler, removeHandler[, scheduler=Scheduler.default])

		Returns an :class:`Observable` that calls ``addHandler(onNext)``
		when the first :class:`Observer <rx.observer.Observer>` subscribes.
		Further subscriber share the same underlying handler.

		When the last subscriber unsubscribes, ``removeHandler(onNext)`` is called.


Imperative
----------

.. class:: Observable

	.. staticmethod:: case(selector, sources[, defaultSource=None])
					  case(selector, sources[, scheduler=Scheduler.constantTimeOperations])

		Subscribes :class:`Observer <rx.observer.Observer>` to
		``sources[selector()]``. If the key returned by ``selector()``
		is not found in ``sources`` then the observer is subscribed to
		``defaultSource``.

		If ``defaultSource == None`` then
		``defaultSource = Observable.empty(scheduler)``.

	.. staticmethod:: iterableFor(iterable, resultSelector)

		Iterates over ``iterable`` and Concatenates all :class:`Observable`s
		returned by ``resultSelector(iterationValue)``

	.. staticmethod:: branch(condition, thenSource[, elseSource=None])
					  branch(condition, thenSource[, scheduler=Scheduler.constantTimeOperations])

		Subscribes :class:`Observer <rx.observer.Observer>` to ``thenSource`` if
		``condition()`` returns ``True`` otherwise to ``elseSource``.

		If ``elseSource == None`` then ``elseSource = Observable.empty(scheduler)``.

	.. method:: doWhile(condition)

		Resubscribes :class:`Observer <rx.observer.Observer>` to ``self``
		on completion as long as ``condition()`` returns ``True`` and at least once.

	.. method:: loop(condition)

		Resubscribes :class:`Observer <rx.observer.Observer>` to ``self``
		on completion as long as ``condition()`` returns ``True``.


Multiple
--------

.. class:: Observable

	.. method:: amb(*others)

		Subscribes :class:`Observer <rx.observer.Observer>` to the first
		:class:`Observable` that yields a value including ``self``.

	.. staticmethod:: amb(first, *others)

		See :meth:`amb`.

	.. method:: catchException(handler[, exceptionType=Exception])

		Continues an :class:`Observable` that is terminated by an exception
		that is an instance of ``exceptionType`` with the :class:`Observable` produced
		by the ``handler``.

	.. method:: catchFallback(*sources)

		Continues an :class:`Observable` that is terminated by an exception
		with the next :class:`Observable`.

	.. method:: concat(*sources)

		Concatenates all :class:`Observable` values in ``sources``.

	.. staticmethod:: concat(*sources)

		See :meth:`concat`.

	.. method:: merge([maxConcurrency=0])

		Merges all :class:`Observable` values in an :class:`Observable`.

	.. staticmethod:: onErrorResumeNext(*sources)

		Continues an :class:`Observable` that is terminated normally or by an
		exception with the next :class:`Observable`.

	.. method:: skipUntil(other)

		Skips values until ``other`` yields the first value or completes.

	.. method:: skipUntil(time[, scheduler=Scheduler.timeBasedOperation])

		Skips values until the timer created on ``scheduler`` completes
		after ``time``.

	.. method:: switch()

		Transforms an :class:`Observable` of :class:`Observable` values
		into an :class:`Observable` producing values only from the most
		recent :class:`Observable`.

	.. method:: takeUntil(other)

		Takes values until ``other`` yields the first value or completes.

	.. method:: takeUntil(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values until the timer created on ``scheduler`` completes
		after ``time``.

	.. method:: zip(*others[, resultSelector=lambda *x: tuple(x)])

		Merges all :class:`Observable` into one observable sequence by
		combining their elements in a pairwise fashion.

	.. staticmethod:: zip(*sources[, resultSelector=lambda *x: tuple(x)])

		See :meth:`zip(*others)`


Single
------

.. class:: Observable

	.. method:: asObservable()

		Hides the original type of the :class:`Observable`.

	.. method:: buffer(count[, skip=count])

		Buffers ``count`` values and yields the as list. Creates
		a new buffer every ``skip`` values.

	.. method:: dematerialize()

		Turns an :class:`Observable` of
		:class:`Notification <rx.notification.Notification>` values
		into and :class:`Observable` representing this notifications.

	.. method:: do([onNext=noop, onError=noop, onCompleted=noop])

		Invoke ``onNext`` on each value, ``onError`` on exception and
		``onComplete`` on completion of the :class:`Observable`.

	.. method:: doFinally(action)

		Invokes ``action`` if the :class:`Observable` completes normally
		or exceptionally.

	.. method:: ignoreElements()

		Returns an :class:`Observable` that ignores all values of the original
		:class:`Observable`.

	.. method:: materialize()

		Turns values, exception and completion into
		:class:`Notification <rx.notification.Notification>` values.
		Completes when the original :class:`Observable` completes normally or
		exceptionally.

	.. method:: repeatSelf([count=indefinite])

		Repeats the original :class:`Observable` ``count`` times.

	.. method:: retry([count=indefinite])

		Retries the original :class:`Observable` ``count`` times until
		it does not complete exceptionally.

	.. method:: scan([seed=None, accumulator=None])

		Applies ``accumulator`` over the values of the :class:`Observable`
		and yields each intermediate result

	.. method:: skipLast(count)

		Skips the last ``count`` values.

	.. method:: skipLastWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Skips values starting ``time`` before the :class:`Observable` completes.
		Values are yielded on ``scheduler``.

	.. method:: startWith(*values)

		Prepends ``values`` to the :class:`Observable`.

	.. method:: takeLast(count)

		Takes the last ``count`` values.

	.. method:: takeLastWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values starting ``time`` before the :class:`Observable` completes.
		Values are yielded on ``scheduler``.

	.. method:: takeLast(count)

		Takes the last ``count`` values and yields them as list.

	.. method:: takeLastWithTime(time[, scheduler=Scheduler.timeBasedOperation])

		Takes values starting ``time`` before the :class:`Observable` completes
		and yields them as list

	.. method:: window(count[, skip=count])

		Yields an :class:`Observable` every ``skip`` values that yields
		it self the next ``count`` values.






















